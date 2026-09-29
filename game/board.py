from game.pieces import (
    peca_existe,
    tipo_da_peca,
    nome_da_peca,
)


class Board:

    LOCAIS = (
        "arvore",
        "parquinho",
        "lago",
        "ponto",
    )

    TIPOS = (
        "morador",
        "cor",
        "animal",
        "hobby",
    )

    def __init__(self):
        self.slots = self._criar_slots()

    def _criar_slots(self):

        return {
            local: {
                tipo: None
                for tipo in self.TIPOS
            }
            for local in self.LOCAIS
        }

    # ========================================================
    # COLOCAR PEÇA
    # ========================================================

    def colocar_peca(self, local, tipo, peca):

        self._validar_slot(local, tipo)

        # A peça precisa existir no catálogo.
        if not peca_existe(peca):

            print(
                f"\n❌ Peça desconhecida: {peca}"
            )

            return False

        # O tipo físico da peça precisa corresponder
        # ao tipo daquele slot.
        tipo_real = tipo_da_peca(peca)

        if tipo_real != tipo:

            print(
                f"\n❌ PEÇA INCOMPATÍVEL!"
            )

            print(
                f"{nome_da_peca(peca)} é do tipo "
                f"{tipo_real.upper()}."
            )

            print(
                f"Este slot aceita apenas "
                f"{tipo.upper()}."
            )

            return False

        # A mesma peça não pode ocupar dois slots.
        posicao_existente = (
            self.localizar_peca(peca)
        )

        if posicao_existente is not None:

            local_atual, tipo_atual = (
                posicao_existente
            )

            # Se já está exatamente neste slot,
            # não precisamos fazer nada.
            if (
                local_atual == local
                and tipo_atual == tipo
            ):

                return True

            print(
                f"\n❌ PEÇA JÁ ESTÁ NA MESA!"
            )

            print(
                f"{nome_da_peca(peca)} já está em "
                f"{local_atual.upper()} / "
                f"{tipo_atual.upper()}."
            )

            return False

        # Se já houver outra peça nesse slot,
        # ela é substituída.
        anterior = self.slots[local][tipo]

        if anterior is not None:

            print(
                f"\n🔄 {nome_da_peca(anterior)} "
                f"foi substituído por "
                f"{nome_da_peca(peca)}."
            )

        self.slots[local][tipo] = peca

        print(
            f"\n🟢 {local.upper()} / "
            f"{tipo.upper()} → "
            f"{nome_da_peca(peca)}"
        )

        return True

    # ========================================================
    # RETIRAR PEÇA
    # ========================================================

    def retirar_peca(self, local, tipo):

        self._validar_slot(local, tipo)

        peca = self.slots[local][tipo]

        self.slots[local][tipo] = None

        if peca is not None:

            print(
                f"\n⚪ {local.upper()} / "
                f"{tipo.upper()} → "
                f"{nome_da_peca(peca)} RETIRADO"
            )

        return peca

    # ========================================================
    # LOCALIZAR PEÇA
    # ========================================================

    def localizar_peca(self, peca):

        for local in self.LOCAIS:

            for tipo in self.TIPOS:

                if self.slots[local][tipo] == peca:

                    return local, tipo

        return None

    # ========================================================
    # CONSULTAS
    # ========================================================

    def obter_peca(self, local, tipo):

        self._validar_slot(local, tipo)

        return self.slots[local][tipo]

    def quantidade_pecas(self):

        return sum(
            1
            for local in self.slots.values()
            for peca in local.values()
            if peca is not None
        )

    def completa(self):

        return self.quantidade_pecas() == 16

    def vazia(self):

        return self.quantidade_pecas() == 0

    # ========================================================
    # LIMPEZA
    # ========================================================

    def limpar(self):

        for local in self.LOCAIS:

            for tipo in self.TIPOS:

                self.slots[local][tipo] = None

    # ========================================================
    # VALIDAÇÃO DE SLOT
    # ========================================================

    def _validar_slot(self, local, tipo):

        if local not in self.LOCAIS:

            raise ValueError(
                f"Local inválido: {local}"
            )

        if tipo not in self.TIPOS:

            raise ValueError(
                f"Tipo inválido: {tipo}"
            )

    # ========================================================
    # VISUALIZAÇÃO
    # ========================================================

    def mostrar(self):

        print("\n" + "=" * 75)
        print("MESA VIRTUAL")
        print("=" * 75)

        for local in self.LOCAIS:

            dados = self.slots[local]

            print(
                f"\n{local.upper()}"
            )

            print(
                f"  Morador : "
                f"{nome_da_peca(dados['morador']) if dados['morador'] else '---'}"
            )

            print(
                f"  Cor     : "
                f"{nome_da_peca(dados['cor']) if dados['cor'] else '---'}"
            )

            print(
                f"  Animal  : "
                f"{nome_da_peca(dados['animal']) if dados['animal'] else '---'}"
            )

            print(
                f"  Hobby   : "
                f"{nome_da_peca(dados['hobby']) if dados['hobby'] else '---'}"
            )

        print(
            f"\nPeças posicionadas: "
            f"{self.quantidade_pecas()}/16"
        )

        print("=" * 75)