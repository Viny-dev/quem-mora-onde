PECAS = {
    # ========================================================
    # MORADORES
    # ========================================================
    "lucas": {
        "nome": "Lucas",
        "tipo": "morador",
    },
    "ana": {
        "nome": "Ana",
        "tipo": "morador",
    },
    "carlos": {
        "nome": "Carlos",
        "tipo": "morador",
    },
    "debora": {
        "nome": "Débora",
        "tipo": "morador",
    },

    # ========================================================
    # CORES
    # ========================================================
    "amarela": {
        "nome": "Amarela",
        "tipo": "cor",
    },
    "azul": {
        "nome": "Azul",
        "tipo": "cor",
    },
    "verde": {
        "nome": "Verde",
        "tipo": "cor",
    },
    "vermelha": {
        "nome": "Vermelha",
        "tipo": "cor",
    },

    # ========================================================
    # ANIMAIS
    # ========================================================
    "coelho": {
        "nome": "Coelho",
        "tipo": "animal",
    },
    "cachorro": {
        "nome": "Cachorro",
        "tipo": "animal",
    },
    "tartaruga": {
        "nome": "Tartaruga",
        "tipo": "animal",
    },
    "gato": {
        "nome": "Gato",
        "tipo": "animal",
    },

    # ========================================================
    # HOBBIES
    # ========================================================
    "livro": {
        "nome": "Livro",
        "tipo": "hobby",
    },
    "bicicleta": {
        "nome": "Bicicleta",
        "tipo": "hobby",
    },
    "bola": {
        "nome": "Bola",
        "tipo": "hobby",
    },
    "violao": {
        "nome": "Violão",
        "tipo": "hobby",
    },
}


def obter_peca(codigo):
    return PECAS.get(codigo)


def peca_existe(codigo):
    return codigo in PECAS


def tipo_da_peca(codigo):

    peca = obter_peca(codigo)

    if peca is None:
        return None

    return peca["tipo"]


def nome_da_peca(codigo):

    peca = obter_peca(codigo)

    if peca is None:
        return codigo

    return peca["nome"]