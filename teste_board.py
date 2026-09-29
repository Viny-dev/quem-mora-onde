from game.board import Board


mesa = Board()

print("\n=== TESTE DA MESA VIRTUAL ===")

mesa.mostrar()

input("\nENTER para colocar Lucas na árvore...")

mesa.colocar_peca(
    "arvore",
    "morador",
    "lucas",
)

mesa.mostrar()

input("\nENTER para colocar a casa amarela...")

mesa.colocar_peca(
    "arvore",
    "cor",
    "amarela",
)

mesa.mostrar()

input("\nENTER para colocar o coelho...")

mesa.colocar_peca(
    "arvore",
    "animal",
    "coelho",
)

mesa.mostrar()

input("\nENTER para colocar o livro...")

mesa.colocar_peca(
    "arvore",
    "hobby",
    "livro",
)

mesa.mostrar()

input("\nENTER para retirar Lucas...")

mesa.retirar_peca(
    "arvore",
    "morador",
)

mesa.mostrar()

print("\n=== FIM DO TESTE ===")