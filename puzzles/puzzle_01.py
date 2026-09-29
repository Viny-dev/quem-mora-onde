NOME = "Puzzle 01"


# ============================================================
# TEXTOS QUE SERÃO EXIBIDOS NA TV
# ============================================================

PISTAS_TV = [
    "Quem gosta de ler também cuida de um coelho.",
    "O cachorro mora com quem gosta de andar de bicicleta.",
    "A casa azul é de quem gosta de andar de bicicleta.",
    "O gato mora na casa vermelha.",
    "Quem joga bola mora na casa verde.",
    "Carlos não tem cachorro nem gato.",
    "Lucas não mora na casa azul nem na verde.",
    "Débora não mora perto da árvore nem do lago.",
    "Carlos mora próximo ao lago.",
    "Ana não mora perto da árvore.",
    "Quem mora perto do ponto de ônibus gosta de tocar violão.",
    "Débora não mora na casa azul.",
]


# ============================================================
# GABARITO DO PUZZLE
# ============================================================

SOLUCAO = {
    "arvore": {
        "morador": "lucas",
        "cor": "amarela",
        "animal": "coelho",
        "hobby": "livro",
    },

    "parquinho": {
        "morador": "ana",
        "cor": "azul",
        "animal": "cachorro",
        "hobby": "bicicleta",
    },

    "lago": {
        "morador": "carlos",
        "cor": "verde",
        "animal": "tartaruga",
        "hobby": "bola",
    },

    "ponto": {
        "morador": "debora",
        "cor": "vermelha",
        "animal": "gato",
        "hobby": "violao",
    },
}


# ============================================================
# REGRAS LÓGICAS
# ============================================================

def validar(moradores, cores, animais, hobbies):

    # 1. Quem gosta de ler também cuida de um coelho.
    if hobbies["livro"] != animais["coelho"]:
        return False

    # 2. O cachorro mora com quem gosta de andar de bicicleta.
    if animais["cachorro"] != hobbies["bicicleta"]:
        return False

    # 3. A casa azul é de quem gosta de andar de bicicleta.
    if cores["azul"] != hobbies["bicicleta"]:
        return False

    # 4. O gato mora na casa vermelha.
    if animais["gato"] != cores["vermelha"]:
        return False

    # 5. Quem joga bola mora na casa verde.
    if hobbies["bola"] != cores["verde"]:
        return False

    # 6. Carlos não tem cachorro nem gato.
    if moradores["carlos"] in (
        animais["cachorro"],
        animais["gato"],
    ):
        return False

    # 7. Lucas não mora na casa azul nem na verde.
    if moradores["lucas"] in (
        cores["azul"],
        cores["verde"],
    ):
        return False

    # 8. Débora não mora perto da árvore nem do lago.
    if moradores["debora"] in (
        "arvore",
        "lago",
    ):
        return False

    # 9. Carlos mora próximo ao lago.
    if moradores["carlos"] != "lago":
        return False

    # 10. Ana não mora perto da árvore.
    if moradores["ana"] == "arvore":
        return False

    # 11. Quem mora perto do ponto de ônibus gosta de tocar violão.
    if hobbies["violao"] != "ponto":
        return False

    # 12. Débora não mora na casa azul.
    if moradores["debora"] == cores["azul"]:
        return False

    return True