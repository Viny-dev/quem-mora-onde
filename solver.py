from itertools import permutations

from puzzles import puzzle_01, puzzle_02, puzzle_03


LOCAIS = (
    "arvore",
    "parquinho",
    "lago",
    "ponto",
)

MORADORES = (
    "lucas",
    "ana",
    "carlos",
    "debora",
)

CORES = (
    "amarela",
    "azul",
    "verde",
    "vermelha",
)

ANIMAIS = (
    "coelho",
    "cachorro",
    "tartaruga",
    "gato",
)

HOBBIES = (
    "livro",
    "bicicleta",
    "bola",
    "violao",
)


def gerar_mapeamento(itens, ordem):
    return dict(zip(itens, ordem))


def encontrar_item_no_local(mapeamento, local):
    for item, item_local in mapeamento.items():
        if item_local == local:
            return item

    return "?"


def buscar_solucoes(puzzle):

    solucoes = []
    combinacoes_testadas = 0

    for ordem_moradores in permutations(LOCAIS):

        moradores = gerar_mapeamento(
            MORADORES,
            ordem_moradores,
        )

        for ordem_cores in permutations(LOCAIS):

            cores = gerar_mapeamento(
                CORES,
                ordem_cores,
            )

            for ordem_animais in permutations(LOCAIS):

                animais = gerar_mapeamento(
                    ANIMAIS,
                    ordem_animais,
                )

                for ordem_hobbies in permutations(LOCAIS):

                    hobbies = gerar_mapeamento(
                        HOBBIES,
                        ordem_hobbies,
                    )

                    combinacoes_testadas += 1

                    if puzzle.validar(
                        moradores,
                        cores,
                        animais,
                        hobbies,
                    ):
                        solucoes.append({
                            "moradores": moradores.copy(),
                            "cores": cores.copy(),
                            "animais": animais.copy(),
                            "hobbies": hobbies.copy(),
                        })

    return solucoes, combinacoes_testadas


def mostrar_solucao(solucao):

    print("\nSOLUÇÃO ENCONTRADA:\n")

    print(
        f"{'LOCAL':<15}"
        f"{'MORADOR':<12}"
        f"{'COR':<12}"
        f"{'ANIMAL':<14}"
        f"{'HOBBY':<12}"
    )

    print("-" * 65)

    for local in LOCAIS:

        morador = encontrar_item_no_local(
            solucao["moradores"],
            local,
        )

        cor = encontrar_item_no_local(
            solucao["cores"],
            local,
        )

        animal = encontrar_item_no_local(
            solucao["animais"],
            local,
        )

        hobby = encontrar_item_no_local(
            solucao["hobbies"],
            local,
        )

        print(
            f"{local.upper():<15}"
            f"{morador.capitalize():<12}"
            f"{cor.capitalize():<12}"
            f"{animal.capitalize():<14}"
            f"{hobby.capitalize():<12}"
        )


def validar_gabarito(puzzle, solucao_encontrada):
    """
    Além de verificar que existe apenas uma solução,
    confirma que ela é exatamente o gabarito cadastrado.
    """

    for local, esperado in puzzle.SOLUCAO.items():

        morador = encontrar_item_no_local(
            solucao_encontrada["moradores"],
            local,
        )

        cor = encontrar_item_no_local(
            solucao_encontrada["cores"],
            local,
        )

        animal = encontrar_item_no_local(
            solucao_encontrada["animais"],
            local,
        )

        hobby = encontrar_item_no_local(
            solucao_encontrada["hobbies"],
            local,
        )

        encontrado = {
            "morador": morador,
            "cor": cor,
            "animal": animal,
            "hobby": hobby,
        }

        if encontrado != esperado:
            return False

    return True


def executar_solver(puzzle):

    print("\n" + "=" * 65)
    print("QUEM MORA ONDE? - VALIDADOR DE PUZZLES")
    print("=" * 65)

    print(f"\n{puzzle.NOME}")

    solucoes, combinacoes = buscar_solucoes(puzzle)

    print(f"Combinações testadas: {combinacoes:,}")
    print(f"Soluções encontradas: {len(solucoes)}")

    if len(solucoes) == 0:

        print("\n❌ PUZZLE INVÁLIDO")
        print("As pistas são contraditórias.")

        return

    if len(solucoes) > 1:

        print("\n⚠️ PUZZLE AMBÍGUO")
        print(
            f"Existem {len(solucoes)} soluções possíveis."
        )

        return

    print("\n✅ Existe exatamente uma solução.")

    solucao = solucoes[0]

    mostrar_solucao(solucao)

    if validar_gabarito(puzzle, solucao):

        print("\n✅ GABARITO CONFIRMADO")
        print(
            "A solução encontrada é exatamente "
            "a solução cadastrada."
        )

    else:

        print("\n❌ ERRO DE GABARITO")
        print(
            "As pistas possuem uma solução única, "
            "mas ela é diferente do gabarito cadastrado."
        )


if __name__ == "__main__":

    puzzles = [
        puzzle_01,
        puzzle_02,
        puzzle_03,
    ]

    for puzzle in puzzles:
        executar_solver(puzzle)