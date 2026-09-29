"""Polling PC/SC em uma unica thread iniciada pelo lifespan da API."""

import logging
from threading import Event, Lock, Thread
from time import perf_counter

from smartcard.Exceptions import CardConnectionException, NoCardException
from smartcard.System import readers

from game.runtime import game
from nfc.config import APDU_UID, CARTOES, INTERVALO, LEITORES
from nfc.windows import ResolvedorWindows
from nfc.perf import medir

logger = logging.getLogger("uvicorn.error")


class UIDReadError(CardConnectionException):
    """APDU respondeu sem UID valido; nao significa mudanca de topologia."""


class NFCManager:
    def __init__(self):
        self._stop = Event()
        self._lock = Lock()
        self._thread = None
        self._uids = {}
        self._falhas = {}
        self._colocadas = {}
        self._avisos = {}
        self._resolvedor = None
        self._mapeamento = {}
        self._diagnostico = ("inicializando", 0)
        self._inicio = perf_counter()
        self._primeiro_pronto = False

    def start(self):
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._diagnostico = ("inicializando", 0)
            self._inicio = perf_counter()
            self._primeiro_pronto = False
            self._stop.clear()
            self._thread = Thread(target=self._run, name="nfc-monitor", daemon=True)
            self._thread.start()

    def stop(self):
        with self._lock:
            self._stop.set()
            thread = self._thread
        # Espera fora do lock; start ainda ve a thread viva durante o shutdown.
        if thread is not None:
            thread.join()
        with self._lock:
            if self._thread is thread:
                self._thread = None

    def diagnostico(self):
        # Snapshot unico, publicado pela thread NFC; sem lock durante I/O.
        status, prontos = self._diagnostico
        return {"nfc_status": status, "nfc_leitores_prontos": prontos,
                "nfc_leitores_total": len(LEITORES)}

    def _publicar_status(self, disponiveis, concluida=False, falha=False):
        prontos = sum(nome in disponiveis for nome in LEITORES)
        status = ("pronto" if prontos == len(LEITORES) and not falha else
                  "degradado" if concluida or falha or self._primeiro_pronto else
                  "inicializando")
        novo = (status, prontos)
        if novo != self._diagnostico:
            logger.info("NFC: %s (%s/%s leitores)", status, prontos, len(LEITORES))
        self._diagnostico = novo
        if status == "pronto" and not self._primeiro_pronto:
            self._primeiro_pronto = True
            logger.info("NFC: warm-up concluido em %.1f ms; %s descoberta(s) PnP",
                        (perf_counter() - self._inicio) * 1000,
                        self._resolvedor.descobertas)

    def _aviso(self, chave, mensagem):
        if self._avisos.get(chave) != mensagem:
            logger.warning("NFC: %s", mensagem)
            self._avisos[chave] = mensagem

    def _ler_uid(self, leitor):
        with medir("createConnection", str(leitor)):
            conexao = leitor.createConnection()
        try:
            with medir("connect", str(leitor)):
                conexao.connect()
            with medir("UID", str(leitor)):
                dados, sw1, sw2 = conexao.transmit(APDU_UID)
            if (sw1, sw2) != (0x90, 0x00) or not dados:
                raise UIDReadError(
                    f"Resposta UID invalida: {sw1:02X} {sw2:02X}"
                )
            return " ".join(f"{byte:02X}" for byte in dados)
        finally:
            try:
                with medir("disconnect", str(leitor)):
                    conexao.disconnect()
            except Exception:
                logger.debug("NFC: falha ao liberar conexao", exc_info=True)

    def _atualizar(self, nome, slot, uid):
        if self._uids.get(nome) == uid:
            return
        anterior = self._uids.get(nome)
        self._uids[nome] = uid
        colocada = self._colocadas.pop(nome, None)
        local, tipo = slot["local"], slot["tipo"]
        if anterior is not None:
            logger.info("NFC: retirado %s de %s", anterior, nome)
        # Nao remover pecas cuja colocacao foi rejeitada ou alteradas via /dev.
        if colocada is not None and game.board.obter_peca(local, tipo) == colocada:
            game.retirar_peca(local, tipo)
        if uid is None:
            return
        peca = CARTOES.get(uid)
        if peca is None:
            logger.warning("NFC: cartao desconhecido %s em %s", uid, nome)
            return
        logger.info("NFC: %s -> %s em %s/%s", uid, peca, local, tipo)
        if game.colocar_peca(local, tipo, peca):
            self._colocadas[nome] = peca
        else:
            logger.info("NFC: colocacao rejeitada; retire e reapresente o cartao")

    def _confirmar_leitura(self, nome, slot, uid):
        if uid is None:
            self._falhas[nome] = self._falhas.get(nome, 0) + 1
            if self._falhas[nome] < 3:
                return
        else:
            self._falhas.pop(nome, None)
        with medir("atualizar_GameEngine", nome):
            self._atualizar(nome, slot, uid)

    def _poll(self):
        with medir("readers"):
            leitores = readers()
        with medir("resolver_cache"):
            disponiveis = dict(self._resolvedor.resolver(leitores))
        self._publicar_status(disponiveis, self._resolvedor.tentativa_concluida)
        for nome, slot in LEITORES.items():
            if self._stop.is_set():
                return
            leitor = disponiveis.get(nome)
            if leitor is None:
                if self._diagnostico[0] != "inicializando":
                    self._aviso(nome, f"leitor ausente: {nome}; aguardando reconexao")
                # Sem leitor resolvido nao ha evidencia de retirada fisica.
                self._falhas.pop(nome, None)
                self._mapeamento.pop(nome, None)
                continue
            if self._mapeamento.get(nome) != str(leitor):
                logger.info("NFC: %s -> %s -> %s/%s", nome, leitor, slot["local"], slot["tipo"])
                self._mapeamento[nome] = str(leitor)
            try:
                uid = self._ler_uid(leitor)
            except NoCardException:
                uid = None
            except CardConnectionException as erro:
                if not isinstance(erro, UIDReadError):
                    self._resolvedor.invalidar(nome)
                    disponiveis.pop(nome, None)
                    self._publicar_status(disponiveis, falha=True)
                # Uma falha isolada (inclusive 63 00) nao comprova retirada.
                self._aviso(nome, f"falha de conexao em {nome}: {erro}")
                if not self._stop.is_set():
                    self._confirmar_leitura(nome, slot, None)
                continue
            except Exception as erro:
                # Uma falha inesperada de um leitor nao impede consultar o outro.
                self._resolvedor.invalidar(nome)
                disponiveis.pop(nome, None)
                self._publicar_status(disponiveis, falha=True)
                self._falhas.pop(nome, None)
                self._aviso(nome, f"leitor indisponivel em {nome}: {erro}")
                continue
            self._avisos.pop(nome, None)
            if not self._stop.is_set():
                self._confirmar_leitura(nome, slot, uid)

    def _run(self):
        self._resolvedor = ResolvedorWindows(paths=LEITORES)
        logger.info("NFC: inicializando (%s leitores configurados)", len(LEITORES))
        try:
            while not self._stop.is_set():
                try:
                    self._poll()
                    self._avisos.pop("monitor", None)
                except Exception as erro:
                    self._publicar_status({}, falha=True)
                    self._aviso("monitor", f"monitor indisponivel; tentando novamente: {erro}")
                self._stop.wait(INTERVALO)
        finally:
            self._publicar_status({}, falha=True)
            self._resolvedor.close()
            self._resolvedor = None
            logger.info("NFC: monitor encerrado")
