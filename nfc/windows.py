"""Resolve LocationPaths via uma descoberta PnP e associacao oficial PC/SC."""

import ctypes
from ctypes import wintypes
import json
import logging
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

from nfc.perf import medir

logger = logging.getLogger("uvicorn.error")

COMANDO = r"""
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$devices = Get-PnpDevice -PresentOnly -Class SmartCardReader | Where-Object {
    $_.FriendlyName -eq 'ACR122 Smart Card Reader'
}
$result = @($devices | ForEach-Object {
    $paths = Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_LocationPaths'
    [pscustomobject]@{ instance = $_.InstanceId; paths = @($paths.Data) }
})
ConvertTo-Json -InputObject $result -Depth 5 -Compress
"""


def descobrir():
    with medir("resolver_locationpath"):
        resultado = subprocess.run(
            ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', COMANDO],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            check=True, timeout=15, creationflags=subprocess.CREATE_NO_WINDOW,
        )
        dispositivos = json.loads(resultado.stdout)
        associar_pcsc(dispositivos)
        return relacionar(dispositivos)



def associar_pcsc(dispositivos):
    """Windows 8+: nome PC/SC por InstanceId USB, sem cartao/ScFilter.

    InstanceId e usado somente nesta descoberta; a chave persistente e LocationPath.
    Uma consulta PnP, um contexto PC/SC, sem conectar ou transmitir APDUs.
    """
    dll = ctypes.WinDLL("winscard.dll")
    contexto = ctypes.c_size_t()
    dll.SCardEstablishContext.argtypes = [wintypes.DWORD, ctypes.c_void_p,
                                        ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t)]
    dll.SCardEstablishContext.restype = wintypes.LONG
    dll.SCardReleaseContext.argtypes = [ctypes.c_size_t]
    dll.SCardReleaseContext.restype = wintypes.LONG
    listar = dll.SCardListReadersWithDeviceInstanceIdW
    listar.argtypes = [ctypes.c_size_t, wintypes.LPCWSTR, wintypes.LPWSTR,
                       ctypes.POINTER(wintypes.DWORD)]
    listar.restype = wintypes.LONG

    def verificar(codigo):
        if codigo:
            raise RuntimeError(f"Associacao PnP/PCSC falhou: {codigo & 0xffffffff:08X}")

    verificar(dll.SCardEstablishContext(2, None, None, ctypes.byref(contexto)))
    try:
        for dispositivo in dispositivos:
            tamanho = wintypes.DWORD()
            codigo = listar(contexto, dispositivo["instance"], None, ctypes.byref(tamanho))
            if codigo & 0xffffffff == 0x8010002E:  # SCARD_E_NO_READERS_AVAILABLE
                dispositivo["nomes"] = []
                continue
            verificar(codigo)
            buffer = ctypes.create_unicode_buffer(max(tamanho.value, 2))
            verificar(listar(contexto, dispositivo["instance"], buffer, ctypes.byref(tamanho)))
            dispositivo["nomes"] = [nome for nome in buffer[:tamanho.value].split("\0") if nome]
    finally:
        dll.SCardReleaseContext(contexto)


def relacionar(dispositivos):
    """Produz LocationPath -> PC/SC; nenhum ID transitorio e persistido."""
    mapa = {}
    for dispositivo in dispositivos:
        nomes = set(dispositivo.get('nomes', []))
        for relacao in (() if 'nomes' in dispositivo else dispositivo['relations']):
            match = re.search(r'&([^\\&]+)_SCFILTER_', relacao, re.IGNORECASE)
            if match:
                nomes.add(match.group(1).replace('_', ' '))
        if len(nomes) > 1:
            raise ValueError('Associacao PC/SC ambigua para um leitor USB')
        if not nomes:
            continue  # Windows pode ainda estar enumerando o leitor.
        nome = nomes.pop()
        for path in dispositivo['paths']:
            if path in mapa and mapa[path] != nome:
                raise ValueError(f'LocationPath ambiguo: {path}')
            mapa[path] = nome
    return mapa


class ResolvedorWindows:
    """Atualiza PnP em segundo plano sem interromper o polling dos cartoes."""
    def __init__(self, paths=None):
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='nfc-pnp')
        self._future = None
        self._mapa = {}
        self._nomes = None
        self._proxima = 0
        self._geracao = None
        self._topologia = 0
        self._pendente = True
        self._paths = frozenset(paths) if paths is not None else None
        self.tentativa_concluida = False
        self.descobertas = 0
        self._motivo = "startup"

    def resolver(self, leitores):
        nomes = frozenset(str(r) for r in leitores)
        if nomes != self._nomes:
            self._topologia += 1
            self._nomes = nomes
            self._mapa = {}  # Nunca reutilizar nomes apos mudanca de topologia.
            self._proxima = 0
            self._pendente = True
            self._motivo = "startup" if self._topologia == 1 else "mudanca de topologia"
        if self._future is not None and self._future.done():
            future, self._future = self._future, None
            try:
                mapa = future.result()
            except Exception as erro:
                self.tentativa_concluida = True
                self._motivo = "retry apos erro PnP"
                self._proxima = time.monotonic() + 3
                self._pendente = True
                logger.warning("NFC: descoberta PnP falhou; tentando novamente: %s", erro)
            else:
                if self._geracao == self._topologia:
                    self.tentativa_concluida = True
                    self._mapa = mapa
                    configurados_prontos = self._paths is not None and all(
                        mapa.get(path) in nomes for path in self._paths
                    )
                    # Leitor configurado fisicamente ausente aguarda topologia.
                    # Leitores PC/SC extras nao exigem retry se os nossos estao prontos.
                    self._pendente = (not configurados_prontos and
                                      not nomes.issubset(set(mapa.values())))
                    self._motivo = "enumeracao PnP incompleta"
                    self._proxima = time.monotonic() + 3
            # Um erro PnP nao interrompe a leitura dos paths ainda validos.
        if self._pendente and self._future is None and time.monotonic() >= self._proxima:
            self._geracao = self._topologia
            self.descobertas += 1
            logger.info("NFC: descoberta PnP #%s (%s), mapa unico para todos os leitores",
                        self.descobertas, self._motivo)
            self._future = self._executor.submit(descobrir)
        por_nome = {str(r): r for r in leitores}
        return {path: por_nome[nome] for path, nome in self._mapa.items() if nome in por_nome}

    def invalidar(self, path):
        """Falha real PC/SC: revalidar uma vez, preservando os outros paths."""
        if path in self._mapa:
            self._mapa.pop(path)
            self._topologia += 1  # Descarta descoberta iniciada antes da falha.
            self._pendente = True
            self._motivo = f"falha PC/SC em {path}"
        # _proxima limita retries; nunca criar um subprocesso por leitor/ciclo.

    def close(self):
        self._executor.shutdown(wait=True, cancel_futures=True)
