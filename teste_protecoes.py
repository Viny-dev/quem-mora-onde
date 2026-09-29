from game.board import Board


mesa = Board()


print("\n=== TESTE 1: COELHO NO SLOT DE ANIMAL ===")

mesa.colocar_peca(
    "arvore",
    "animal",
    "coelho",
)


print("\n=== TESTE 2: COELHO NO SLOT DE COR ===")

mesa.colocar_peca(
    "lago",
    "cor",
    "coelho",
)


print("\n=== TESTE 3: MESMO COELHO EM OUTRO LOCAL ===")

mesa.colocar_peca(
    "lago",
    "animal",
    "coelho",
)


print("\n=== TESTE 4: PEÇA INEXISTENTE ===")

mesa.colocar_peca(
    "arvore",
    "morador",
    "banana",
)


print("\n=== ESTADO FINAL ===")

mesa.mostrar()