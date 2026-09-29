import random
import time

from game.board import Board
from puzzles import puzzle_01, puzzle_02, puzzle_03


class GameEngine:

    TEMPO_LIMITE = 15 * 60

    ESTADO_AGUARDANDO = "AGUARDANDO"
    ESTADO_JOGANDO = "JOGANDO"
    ESTADO_AGUARDANDO_RETIRADA = "AGUARDANDO_RETIRADA"

    def __init__(self):

        self.puzzles = [
            puzzle_01,
            puzzle_02,
            puzzle_03,
        ]

        self.puzzle_atual = None
        self.puzzle_anterior = None

        self.estado = self.ESTADO_AGUARDANDO

        self.inicio_partida = None
        self.fim_partida = None

        self.tentativas = 0
        self.resultado_final = None

        # Representação oficial da mesa física.
        self.board = Board()

    # ========================================================
    # PUZZLES
    # ========================================================

    def _sortear_puzzle(self):

        disponiveis = [
            puzzle
            for puzzle in self.puzzles
            if puzzle != self.puzzle_anterior
        ]

        return random.choice(disponiveis)

    # ========================================================
    # PARTIDA
    # ========================================================

    def iniciar_partida(self):

        if self.estado == self.ESTADO_JOGANDO:

            print(
                "\n⚠️ Já existe uma partida em andamento."
            )

            return False

        if self.estado == self.ESTADO_AGUARDANDO_RETIRADA:

            print(
                "\n⚠️ Retire todas as peças da mesa "
                "antes de iniciar uma nova partida."
            )

            print(
                f"Peças restantes: "
                f"{self.board.quantidade_pecas()}/16"
            )

            return False

        if not self.board.vazia():

            print(
                "\n⚠️ A mesa precisa estar vazia "
                "para iniciar uma partida."
            )

            return False

        self.puzzle_atual = self._sortear_puzzle()

        self.estado = self.ESTADO_JOGANDO

        self.inicio_partida = time.monotonic()
        self.fim_partida = None

        self.tentativas = 0
        self.resultado_final = None

        print("\n" + "=" * 60)
        print("NOVA PARTIDA")
        print("=" * 60)

        print(
            f"\nPuzzle sorteado: "
            f"{self.puzzle_atual.NOME}"
        )

        print("Tempo: 15:00")

        print("\nPISTAS:\n")

        for numero, pista in enumerate(
            self.puzzle_atual.PISTAS_TV,
            start=1,
        ):

            print(f"{numero}. {pista}")

        return True

    # ========================================================
    # CRONÔMETRO
    # ========================================================

    def tempo_decorrido(self):

        if self.inicio_partida is None:
            return 0

        if self.fim_partida is not None:

            return int(
                self.fim_partida
                - self.inicio_partida
            )

        return int(
            time.monotonic()
            - self.inicio_partida
        )

    def tempo_restante(self):

        restante = (
            self.TEMPO_LIMITE
            - self.tempo_decorrido()
        )

        return max(0, restante)

    def tempo_formatado(self):

        restante = self.tempo_restante()

        minutos = restante // 60
        segundos = restante % 60

        return f"{minutos:02d}:{segundos:02d}"

    def tempo_decorrido_formatado(self):

        decorrido = self.tempo_decorrido()

        minutos = decorrido // 60
        segundos = decorrido % 60

        return f"{minutos:02d}:{segundos:02d}"

    def tempo_esgotado(self):

        return self.tempo_restante() <= 0

    # ========================================================
    # ENTRADA DE PEÇAS
    # ========================================================

    def colocar_peca(self, local, tipo, peca):

        if self.estado != self.ESTADO_JOGANDO:

            print(
                "\n⚠️ Não é possível colocar peças agora."
            )

            return False

        # A Board é responsável por validar:
        # - local
        # - tipo
        # - existência da peça
        # - compatibilidade
        # - duplicidade
        sucesso = self.board.colocar_peca(
            local,
            tipo,
            peca,
        )

        # Se a Board rejeitou, o Engine também rejeita.
        if not sucesso:

            print(
                "\n⚠️ A peça não foi adicionada à mesa."
            )

            return False

        quantidade = self.board.quantidade_pecas()

        print(
            f"Peças posicionadas: "
            f"{quantidade}/16"
        )

        if self.board.completa():

            print(
                "\n🟢 MESA COMPLETA!"
            )

            print(
                "🔘 Botão VERIFICAR habilitado."
            )

        return True

    def retirar_peca(self, local, tipo):

        # Só permitimos retirada durante a partida
        # ou depois que ela terminou.
        if self.estado not in (
            self.ESTADO_JOGANDO,
            self.ESTADO_AGUARDANDO_RETIRADA,
        ):

            print(
                "\n⚠️ Não é possível retirar peças agora."
            )

            return None

        peca = self.board.retirar_peca(
            local,
            tipo,
        )

        # Slot já estava vazio ou operação inválida.
        if peca is None:
            return None

        quantidade = self.board.quantidade_pecas()

        print(
            f"Peças posicionadas: "
            f"{quantidade}/16"
        )

        # Durante a partida, se a mesa deixar
        # de estar completa, o botão VERIFICAR
        # deve ficar desabilitado.
        if (
            self.estado == self.ESTADO_JOGANDO
            and not self.board.completa()
        ):

            print(
                "⚪ Botão VERIFICAR desabilitado."
            )

        # Depois de vitória ou tempo esgotado,
        # retirar a última peça libera o sistema.
        if (
            self.estado
            == self.ESTADO_AGUARDANDO_RETIRADA
            and self.board.vazia()
        ):

            self._finalizar_retirada()

        return peca

    # ========================================================
    # VERIFICAÇÃO
    # ========================================================

    def verificar(self):

        if self.estado != self.ESTADO_JOGANDO:

            print(
                "\n⚠️ Não existe uma partida "
                "ativa para verificar."
            )

            return False

        if self.tempo_esgotado():

            self._encerrar_por_tempo()

            return False

        if not self.board.completa():

            print(
                "\n⚠️ Ainda faltam peças no bairro!"
            )

            print(
                f"Peças: "
                f"{self.board.quantidade_pecas()}/16"
            )

            return False

        self.tentativas += 1

        if self.board.slots == self.puzzle_atual.SOLUCAO:

            self._registrar_vitoria()

            return True

        print(
            "\n🤔 ALGO NÃO ESTÁ CERTO..."
        )

        print(
            "Observe as pistas e tente novamente!"
        )

        return False

    # ========================================================
    # VITÓRIA
    # ========================================================

    def _registrar_vitoria(self):

        self.fim_partida = time.monotonic()

        self.resultado_final = "VITORIA"

        self.puzzle_anterior = self.puzzle_atual

        self.estado = (
            self.ESTADO_AGUARDANDO_RETIRADA
        )

        print(
            "\n🎉 BAIRRO DESVENDADO!"
        )

        print(
            f"Tempo de conclusão: "
            f"{self.tempo_decorrido_formatado()}"
        )

        print(
            f"Tentativas: "
            f"{self.tentativas}"
        )

        print(
            "\n📦 Retire todas as peças "
            "para liberar a próxima partida."
        )

    # ========================================================
    # TEMPO ESGOTADO
    # ========================================================

    def _encerrar_por_tempo(self):

        self.fim_partida = time.monotonic()

        self.resultado_final = "TEMPO_ESGOTADO"

        self.puzzle_anterior = self.puzzle_atual

        self.estado = (
            self.ESTADO_AGUARDANDO_RETIRADA
        )

        print(
            "\n⏰ TEMPO ESGOTADO!"
        )

        print(
            "Retire todas as peças da mesa "
            "para iniciar uma nova partida."
        )

    # ========================================================
    # RETIRADA FINAL
    # ========================================================

    def _finalizar_retirada(self):

        if not self.board.vazia():
            return False

        self.puzzle_atual = None

        self.estado = self.ESTADO_AGUARDANDO

        self.inicio_partida = None
        self.fim_partida = None

        self.tentativas = 0
        self.resultado_final = None

        print(
            "\n✅ TODAS AS PEÇAS RETIRADAS."
        )

        print(
            "Sistema pronto para uma nova partida."
        )

        return True

    # ========================================================
    # SIMULAÇÕES
    # ========================================================

    def simular_montagem_correta(self):

        if self.estado != self.ESTADO_JOGANDO:

            print(
                "\n⚠️ Não existe partida ativa."
            )

            return False

        for local, dados in (
            self.puzzle_atual.SOLUCAO.items()
        ):

            for tipo, peca in dados.items():

                sucesso = self.colocar_peca(
                    local,
                    tipo,
                    peca,
                )

                if not sucesso:
                    return False

        return True

    def simular_montagem_incorreta(self):

        if self.estado != self.ESTADO_JOGANDO:

            print(
                "\n⚠️ Não existe partida ativa."
            )

            return False

        # Primeiro monta corretamente usando
        # as mesmas validações do GameEngine.
        for local, dados in (
            self.puzzle_atual.SOLUCAO.items()
        ):

            for tipo, peca in dados.items():

                sucesso = self.colocar_peca(
                    local,
                    tipo,
                    peca,
                )

                if not sucesso:
                    return False

        # Depois troca dois moradores diretamente
        # para gerar propositalmente uma solução errada.
        arvore = (
            self.board.slots["arvore"]["morador"]
        )

        lago = (
            self.board.slots["lago"]["morador"]
        )

        self.board.slots["arvore"]["morador"] = lago
        self.board.slots["lago"]["morador"] = arvore

        print(
            "\n❌ Mesa preenchida com "
            "uma configuração incorreta."
        )

        print(
            "Peças posicionadas: 16/16"
        )

        print(
            "🔘 Botão VERIFICAR habilitado."
        )

        return True

    def simular_retirada_das_pecas(self):

        if (
            self.estado
            != self.ESTADO_AGUARDANDO_RETIRADA
        ):

            print(
                "\n⚠️ O sistema não está "
                "aguardando retirada."
            )

            return False

        # Faz uma cópia dos slots ocupados,
        # pois a Board será alterada durante
        # o processo.
        ocupados = []

        for local in self.board.LOCAIS:

            for tipo in self.board.TIPOS:

                if (
                    self.board.obter_peca(
                        local,
                        tipo,
                    )
                    is not None
                ):

                    ocupados.append(
                        (local, tipo)
                    )

        for local, tipo in ocupados:

            self.retirar_peca(
                local,
                tipo,
            )

        return True

    # ========================================================
    # STATUS
    # ========================================================

    def mostrar_status(self):

        print("\n" + "-" * 50)
        print("STATUS DA PARTIDA")
        print("-" * 50)

        print(
            f"Estado: "
            f"{self.estado}"
        )

        if self.puzzle_atual is not None:

            print(
                f"Puzzle: "
                f"{self.puzzle_atual.NOME}"
            )

        if self.inicio_partida is not None:

            print(
                f"Tempo restante: "
                f"{self.tempo_formatado()}"
            )

            print(
                f"Tempo decorrido: "
                f"{self.tempo_decorrido_formatado()}"
            )

        else:

            print("Tempo: --:--")

        print(
            f"Peças posicionadas: "
            f"{self.board.quantidade_pecas()}/16"
        )

        print(
            f"Tentativas: "
            f"{self.tentativas}"
        )

        if self.resultado_final is not None:

            print(
                f"Resultado: "
                f"{self.resultado_final}"
            )