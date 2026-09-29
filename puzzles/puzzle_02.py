NOME = "Puzzle 02"


# ============================================================
# TEXTOS QUE SERÃO EXIBIDOS NA TV
# ============================================================

PISTAS_TV = [
    "Quem tem um gato gosta de andar de bicicleta.",
    "Quem mora na casa verde gosta de jogar bola.",
    "O cachorro mora na casa vermelha.",
    "Lucas não mora na casa azul nem na verde.",
    "Carlos não mora perto do lago nem do ponto de ônibus.",
    "Débora não mora perto da árvore.",
    "Ana não mora perto do ponto de ônibus.",
    "Quem mora perto do ponto de ônibus gosta de tocar violão.",
    "A casa azul fica perto da grande árvore.",
    "O coelho mora perto do parquinho.",
    "Ana não mora na casa amarela.",
    "Quem gosta de ler também tem um cachorro.",
    "Carlos não tem um coelho.",
    "Débora não tem cachorro nem tartaruga.",
]


# ============================================================
# GABARITO DO PUZZLE
# ============================================================

SOLUCAO = {
    "arvore": {
        "morador": "carlos",
        "cor": "azul",
        "animal": "gato",
        "hobby": "bicicleta",
    },

    "parquinho": {
        "morador": "debora",
        "cor": "verde",
        "animal": "coelho",
        "hobby": "bola",
    },

    "lago": {
        "morador": "ana",
        "cor": "vermelha",
        "animal": "cachorro",
        "hobby": "livro",
    },

    "ponto": {
        "morador": "lucas",
        "cor": "amarela",
        "animal": "tartaruga",
        "hobby": "violao",
    },
}


# ============================================================
# REGRAS LÓGICAS
# ============================================================

def validar(moradores, cores, animais, hobbies):

    # 1. Quem tem um gato gosta de andar de bicicleta.
    if animais["gato"] != hobbies["bicicleta"]:
        return False

    # 2. Quem mora na casa verde gosta de jogar bola.
    if cores["verde"] != hobbies["bola"]:
        return False

    # 3. O cachorro mora na casa vermelha.
    if animais["cachorro"] != cores["vermelha"]:
        return False

    # 4. Lucas não mora na casa azul nem na verde.
    if moradores["lucas"] in (
        cores["azul"],
        cores["verde"],
    ):
        return False

    # 5. Carlos não mora perto do lago nem do ponto de ônibus.
    if moradores["carlos"] in (
        "lago",
        "ponto",
    ):
        return False

    # 6. Débora não mora perto da árvore.
    if moradores["debora"] == "arvore":
        return False

    # 7. Ana não mora perto do ponto de ônibus.
    if moradores["ana"] == "ponto":
        return False

    # 8. Quem mora perto do ponto de ônibus gosta de tocar violão.
    if hobbies["violao"] != "ponto":
        return False

    # 9. A casa azul fica perto da grande árvore.
    if cores["azul"] != "arvore":
        return False

    # 10. O coelho mora perto do parquinho.
    if animais["coelho"] != "parquinho":
        return False

    # 11. Ana não mora na casa amarela.
    if moradores["ana"] == cores["amarela"]:
        return False

    # 12. Quem gosta de ler também tem um cachorro.
    if hobbies["livro"] != animais["cachorro"]:
        return False

    # 13. Carlos não tem um coelho.
    if moradores["carlos"] == animais["coelho"]:
        return False

    # 14. Débora não tem cachorro nem tartaruga.
    if moradores["debora"] in (
        animais["cachorro"],
        animais["tartaruga"],
    ):
        return False

    return True