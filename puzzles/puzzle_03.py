NOME = "Puzzle 03"


# ============================================================
# TEXTOS QUE SERÃO EXIBIDOS NA TV
# ============================================================

PISTAS_TV = [
    "Quem tem um gato também gosta de ler.",
    "Quem tem um coelho gosta de andar de bicicleta.",
    "Quem mora na casa azul gosta de jogar bola.",
    "A tartaruga mora na casa verde.",
    "Lucas não mora perto da árvore nem do lago.",
    "Carlos não mora perto da árvore.",
    "Débora não mora perto do parquinho.",
    "Ana não mora na casa vermelha nem na amarela.",
    "A casa amarela fica próxima ao lago.",
    "O cachorro mora perto do ponto de ônibus.",
    "Quem gosta de tocar violão mora perto da grande árvore.",
    "Lucas não tem cachorro nem coelho.",
    "Carlos não tem gato.",
    "Débora não tem cachorro nem tartaruga.",
]


# ============================================================
# GABARITO DO PUZZLE
# ============================================================

SOLUCAO = {
    "arvore": {
        "morador": "ana",
        "cor": "verde",
        "animal": "tartaruga",
        "hobby": "violao",
    },

    "parquinho": {
        "morador": "lucas",
        "cor": "vermelha",
        "animal": "gato",
        "hobby": "livro",
    },

    "lago": {
        "morador": "debora",
        "cor": "amarela",
        "animal": "coelho",
        "hobby": "bicicleta",
    },

    "ponto": {
        "morador": "carlos",
        "cor": "azul",
        "animal": "cachorro",
        "hobby": "bola",
    },
}


# ============================================================
# REGRAS LÓGICAS
# ============================================================

def validar(moradores, cores, animais, hobbies):

    # 1. Quem tem um gato também gosta de ler.
    if animais["gato"] != hobbies["livro"]:
        return False

    # 2. Quem tem um coelho gosta de andar de bicicleta.
    if animais["coelho"] != hobbies["bicicleta"]:
        return False

    # 3. Quem mora na casa azul gosta de jogar bola.
    if cores["azul"] != hobbies["bola"]:
        return False

    # 4. A tartaruga mora na casa verde.
    if animais["tartaruga"] != cores["verde"]:
        return False

    # 5. Lucas não mora perto da árvore nem do lago.
    if moradores["lucas"] in (
        "arvore",
        "lago",
    ):
        return False

    # 6. Carlos não mora perto da árvore.
    if moradores["carlos"] == "arvore":
        return False

    # 7. Débora não mora perto do parquinho.
    if moradores["debora"] == "parquinho":
        return False

    # 8. Ana não mora na casa vermelha nem na amarela.
    if moradores["ana"] in (
        cores["vermelha"],
        cores["amarela"],
    ):
        return False

    # 9. A casa amarela fica próxima ao lago.
    if cores["amarela"] != "lago":
        return False

    # 10. O cachorro mora perto do ponto de ônibus.
    if animais["cachorro"] != "ponto":
        return False

    # 11. Quem gosta de tocar violão mora perto da grande árvore.
    if hobbies["violao"] != "arvore":
        return False

    # 12. Lucas não tem cachorro nem coelho.
    if moradores["lucas"] in (
        animais["cachorro"],
        animais["coelho"],
    ):
        return False

    # 13. Carlos não tem gato.
    if moradores["carlos"] == animais["gato"]:
        return False

    # 14. Débora não tem cachorro nem tartaruga.
    if moradores["debora"] in (
        animais["cachorro"],
        animais["tartaruga"],
    ):
        return False

    return True