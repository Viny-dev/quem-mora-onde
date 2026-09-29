from game.pieces import (
    PECAS,
    obter_peca,
    tipo_da_peca,
    nome_da_peca,
)


print("\n=== CATÁLOGO DE PEÇAS ===\n")

for codigo, dados in PECAS.items():

    print(
        f"{codigo:<12} "
        f"→ {dados['nome']:<12} "
        f"[{dados['tipo']}]"
    )


print("\nTotal:", len(PECAS))


print("\n=== TESTES ===")

print(
    "coelho:",
    obter_peca("coelho"),
)

print(
    "tipo do coelho:",
    tipo_da_peca("coelho"),
)

print(
    "nome de debora:",
    nome_da_peca("debora"),
)

print(
    "peça inexistente:",
    obter_peca("banana"),
)