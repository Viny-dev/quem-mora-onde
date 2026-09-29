import unittest
from concurrent.futures import Future
from unittest.mock import Mock, patch
from backend import api
from nfc.config import LEITORES
from nfc.manager import NFCManager
from nfc.windows import ResolvedorWindows, relacionar


class StartupNFC(unittest.TestCase):
    def setUp(self):
        self.manager = NFCManager()
        self.resolver = ResolvedorWindows(paths=LEITORES)
        self.resolver._executor.shutdown()
        self.resolver._executor = Mock()
        self.future = Future()
        self.resolver._executor.submit.return_value = self.future
        self.manager._resolvedor = self.resolver
        self.paths = list(LEITORES)
        self.leitores = [f'leitor {i}' for i in range(len(self.paths))]
        self.mapa = dict(zip(self.paths, self.leitores))

    def poll(self, leitores):
        with patch('nfc.manager.readers', return_value=leitores), patch.object(self.manager, '_ler_uid', return_value=None):
            self.manager._poll()

    def test_startup_unico_com_leitor_extra(self):
        self.poll(self.leitores + ['extra'])
        self.assertEqual(self.manager.diagnostico()['nfc_status'], 'inicializando')
        self.future.set_result(self.mapa)
        self.poll(self.leitores + ['extra'])
        self.assertEqual(self.manager.diagnostico(), {
            'nfc_status': 'pronto', 'nfc_leitores_prontos': len(LEITORES), 'nfc_leitores_total': len(LEITORES)})
        with patch('nfc.windows.time.monotonic', return_value=10**12):
            for _ in range(20):
                self.poll(self.leitores + ['extra'])
        self.assertEqual(self.resolver.descobertas, 1)

    def test_desconectado_degrada_sem_redescoberta_periodica_e_recupera(self):
        self.poll(self.leitores[:1])
        self.future.set_result({self.paths[0]: self.leitores[0]})
        self.poll(self.leitores[:1])
        self.assertEqual(self.manager.diagnostico()['nfc_status'], 'degradado')
        self.assertEqual(self.manager.diagnostico()['nfc_leitores_prontos'], 1)
        with patch('nfc.windows.time.monotonic', return_value=10**12):
            self.poll(self.leitores[:1])
        self.assertEqual(self.resolver.descobertas, 1)
        retorno = Future()
        self.resolver._executor.submit.return_value = retorno
        self.poll(self.leitores)
        retorno.set_result(self.mapa)
        self.poll(self.leitores)
        self.assertEqual(self.manager.diagnostico()['nfc_status'], 'pronto')
        self.assertEqual(self.resolver.descobertas, 2)

    def test_endpoint_bloqueia_inicio_ate_pronto(self):
        with patch.object(api, 'nfc_manager', self.manager), patch.object(api.game, 'iniciar_partida', return_value=True) as iniciar:
            for status in ['inicializando', 'degradado']:
                self.manager._diagnostico = (status, 0)
                resposta = api.iniciar_partida()
                self.assertFalse(resposta['sucesso'])
                self.assertEqual(resposta['nfc_status'], status)
            iniciar.assert_not_called()
            self.manager._diagnostico = ('pronto', len(LEITORES))
            self.assertTrue(api.iniciar_partida()['sucesso'])
            iniciar.assert_called_once()

    def test_associacao_nao_depende_do_formato_scfilter(self):
        dispositivos = [
            {'paths': [path], 'nomes': [nome], 'relations': ['ScFilter\\7&opaque']}
            for path, nome in self.mapa.items()
        ]
        self.assertEqual(relacionar(dispositivos), self.mapa)

    def test_falha_pnp_degrada(self):
        self.poll(self.leitores)
        self.future.set_exception(RuntimeError('PnP'))
        self.poll(self.leitores)
        self.assertEqual(self.manager.diagnostico()['nfc_status'], 'degradado')


if __name__ == '__main__':
    unittest.main()
