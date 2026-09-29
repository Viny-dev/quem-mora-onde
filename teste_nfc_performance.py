"""Regressoes de cache e concorrencia; nao exige hardware nem httpx."""
import asyncio
import json
import time
import unittest
from concurrent.futures import Future
from threading import Event
from unittest.mock import Mock, patch

from backend import api
from nfc.config import LEITORES
from nfc.manager import NFCManager, UIDReadError
from nfc.windows import ResolvedorWindows


async def get_estado():
    mensagens = []
    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}
    async def send(message):
        mensagens.append(message)
    await api.app({
        "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
        "method": "GET", "scheme": "http", "path": "/estado", "raw_path": b"/estado",
        "query_string": b"", "root_path": "", "headers": [],
        "server": ("test", 80), "client": ("test", 1),
    }, receive, send)
    status = next(m["status"] for m in mensagens if m["type"] == "http.response.start")
    body = b"".join(m.get("body", b"") for m in mensagens if m["type"] == "http.response.body")
    return status, json.loads(body)


class ResponsividadeAPI(unittest.IsolatedAsyncioTestCase):
    async def test_estado_responde_durante_descoberta_windows_lenta(self):
        iniciou, liberar, terminou = Event(), Event(), Event()
        def descoberta_lenta():
            iniciou.set()
            try:
                if not liberar.wait(5):
                    raise TimeoutError("teste nao liberou descoberta")
                return {}
            finally:
                terminou.set()
        manager = NFCManager()
        with patch.object(api, 'nfc_manager', manager), \
             patch('nfc.manager.readers', return_value=['reader']), \
             patch('nfc.windows.descobrir', side_effect=descoberta_lenta) as descobrir:
            async with api.lifespan(api.app):
                try:
                    deadline = time.perf_counter() + 2
                    while not iniciou.is_set():
                        self.assertLess(time.perf_counter(), deadline)
                        await asyncio.sleep(.01)
                    latencias = []
                    for _ in range(5):
                        inicio = time.perf_counter()
                        status, body = await asyncio.wait_for(get_estado(), .5)
                        latencias.append((time.perf_counter() - inicio) * 1000)
                        self.assertEqual(status, 200)
                        self.assertIn('pecas', body)
                        self.assertEqual(body['nfc_status'], 'inicializando')
                        self.assertEqual(body['nfc_leitores_prontos'], 0)
                        self.assertEqual(body['nfc_leitores_total'], len(LEITORES))
                        self.assertFalse(terminou.is_set())
                        await asyncio.sleep(.25)
                    self.assertEqual(descobrir.call_count, 1)
                    print(f"API com PnP bloqueado >1.25s: max GET {max(latencias):.1f} ms")
                finally:
                    liberar.set()


class CacheWindows(unittest.TestCase):
    def setUp(self):
        self.resolver = ResolvedorWindows()
        self.resolver._executor.shutdown()
        self.resolver._executor = Mock()
        self.future = Future()
        self.resolver._executor.submit.return_value = self.future

    def test_16_leitores_uma_descoberta_cache_sem_expiracao_periodica(self):
        nomes = [f'reader {n}' for n in range(16)]
        mapa = {f'path {n}': nome for n, nome in enumerate(nomes)}
        self.resolver.resolver(nomes)
        self.future.set_result(mapa)
        self.assertEqual(self.resolver.resolver(nomes), mapa)
        with patch('nfc.windows.time.monotonic', return_value=10**12):
            for _ in range(100):
                self.assertEqual(self.resolver.resolver(nomes), mapa)
        self.assertEqual(self.resolver._executor.submit.call_count, 1)

    def test_invalidacao_individual_preserva_outro_leitor(self):
        self.resolver.resolver(['A', 'B'])
        self.future.set_result({'pA': 'A', 'pB': 'B'})
        self.resolver.resolver(['A', 'B'])
        self.resolver.invalidar('pA')
        self.resolver._executor.submit.return_value = Future()
        with patch('nfc.windows.time.monotonic', return_value=10**12):
            self.assertEqual(self.resolver.resolver(['A', 'B']), {'pB': 'B'})
            for _ in range(10):
                self.resolver.invalidar('pA')
                self.resolver.resolver(['A', 'B'])
        self.assertEqual(self.resolver._executor.submit.call_count, 2)

    def test_mapa_incompleto_tenta_novamente_sem_tempestade(self):
        self.resolver.resolver(['A', 'B'])
        self.future.set_result({'pA': 'A'})
        self.assertEqual(self.resolver.resolver(['A', 'B']), {'pA': 'A'})
        self.resolver.resolver(['A', 'B'])
        self.assertEqual(self.resolver._executor.submit.call_count, 1)
        self.resolver._executor.submit.return_value = Future()
        with patch('nfc.windows.time.monotonic', return_value=10**12):
            self.resolver.resolver(['A', 'B'])
        self.assertEqual(self.resolver._executor.submit.call_count, 2)

    def test_erro_pnp_preserva_paths_validos(self):
        self.resolver.resolver(['A', 'B'])
        self.future.set_result({'pA': 'A', 'pB': 'B'})
        self.resolver.resolver(['A', 'B'])
        self.resolver.invalidar('pA')
        falha = Future()
        self.resolver._executor.submit.return_value = falha
        with patch('nfc.windows.time.monotonic', return_value=10**12):
            self.resolver.resolver(['A', 'B'])
            falha.set_exception(RuntimeError('PnP temporariamente indisponivel'))
            self.assertEqual(self.resolver.resolver(['A', 'B']), {'pB': 'B'})

    def test_uid_invalido_nao_invalida_topologia(self):
        manager = NFCManager()
        manager._resolvedor = Mock()
        manager._resolvedor.resolver.return_value = dict.fromkeys(LEITORES, 'reader')
        with patch('nfc.manager.readers', return_value=[]), \
             patch.object(manager, '_ler_uid', side_effect=UIDReadError('63 00')):
            manager._poll()
        manager._resolvedor.invalidar.assert_not_called()


if __name__ == '__main__':
    unittest.main()
