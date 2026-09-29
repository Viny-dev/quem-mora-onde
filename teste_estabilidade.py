import unittest
from unittest.mock import Mock, patch
from smartcard.Exceptions import CardConnectionException, NoCardException
from nfc.manager import NFCManager
from nfc.config import LEITORES
from nfc.windows import ResolvedorWindows
from concurrent.futures import Future


class EstabilidadeNFC(unittest.TestCase):
    def setUp(self):
        self.manager = NFCManager()
        self.names = list(LEITORES)
        self.manager._resolvedor = Mock()
        self.manager._resolvedor.resolver.return_value = dict.fromkeys(self.names, 'reader')
        self.manager._atualizar = Mock()

    def poll(self, results):
        with patch('nfc.manager.readers', return_value=[]), patch.object(self.manager, '_ler_uid', side_effect=results):
            self.manager._poll()

    def test_falha_isolada_e_recuperacao(self):
        for failure in (NoCardException('sem cartao', 0), CardConnectionException('Resposta UID invalida: 63 00')):
            self.poll([failure, 'B'])
            self.manager._atualizar.assert_called_with(self.names[1], LEITORES[self.names[1]], 'B')
            self.assertFalse(any(c.args[2] is None for c in self.manager._atualizar.call_args_list))
            self.poll(['A', 'B'])
            self.assertNotIn(self.names[0], self.manager._falhas)

    def test_retirada_confirmada(self):
        self.poll([NoCardException('sem cartao', 0), 'B'])
        self.poll([CardConnectionException('63 00'), 'B'])
        self.assertFalse(any(c.args[2] is None for c in self.manager._atualizar.call_args_list))
        self.poll([NoCardException('sem cartao', 0), 'B'])
        self.manager._atualizar.assert_any_call(self.names[0], LEITORES[self.names[0]], None)

    def test_reconexao_preserva_estado_e_outro_leitor(self):
        self.manager._resolvedor.resolver.return_value.pop(self.names[0])
        self.poll(['B'])
        self.assertEqual(self.manager._atualizar.call_count, 1)
        self.manager._resolvedor.resolver.return_value[self.names[0]] = 'new reader'
        self.poll(['A', 'B'])
        self.manager._atualizar.assert_any_call(self.names[0], LEITORES[self.names[0]], 'A')

    def test_erro_inesperado_isolado(self):
        self.poll([RuntimeError('USB'), 'B'])
        self.manager._atualizar.assert_called_once_with(self.names[1], LEITORES[self.names[1]], 'B')

    def test_topologia_volta_ao_mesmo_nome_descarta_resolucao_antiga(self):
        resolver = ResolvedorWindows()
        resolver._executor.shutdown()
        resolver._executor = Mock()
        old = Future()
        resolver._executor.submit.return_value = old
        resolver.resolver(['A', 'B'])
        resolver.resolver(['B'])
        old.set_result({'path': 'A'})
        self.assertEqual(resolver.resolver(['A', 'B']), {})
        self.assertEqual(resolver._executor.submit.call_count, 2)


if __name__ == '__main__':
    unittest.main()

