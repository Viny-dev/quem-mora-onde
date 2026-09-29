import asyncio
from contextlib import asynccontextmanager, suppress
from time import perf_counter

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from game.runtime import game
from nfc.manager import NFCManager
from nfc.perf import ATIVO, medir, registrar


nfc_manager = NFCManager()


async def medir_event_loop():
    while True:
        inicio = perf_counter()
        await asyncio.sleep(0.1)
        registrar("event_loop_atraso", perf_counter() - inicio - 0.1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    nfc_manager.start()
    monitor_loop = asyncio.create_task(medir_event_loop()) if ATIVO else None
    try:
        yield
    finally:
        if monitor_loop is not None:
            monitor_loop.cancel()
            with suppress(asyncio.CancelledError):
                await monitor_loop
        await asyncio.to_thread(nfc_manager.stop)


app = FastAPI(
    title="Quem Mora Onde? API",
    lifespan=lifespan,
)


class MedirEstado:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"] == "/estado":
            with medir("GET /estado total"):
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)


app.add_middleware(MedirEstado)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MODELOS
# ============================================================

class ColocarPecaRequest(BaseModel):
    local: str
    tipo: str
    peca: str


class RetirarPecaRequest(BaseModel):
    local: str
    tipo: str


# ============================================================
# ESTADO
# ============================================================

def estado_do_jogo():

    puzzle = None
    pistas = []

    if game.puzzle_atual is not None:

        puzzle = game.puzzle_atual.NOME
        pistas = game.puzzle_atual.PISTAS_TV

    return {
        **nfc_manager.diagnostico(),
        "estado": game.estado,
        "puzzle": puzzle,
        "pistas": pistas,

        "tempo_restante": game.tempo_restante(),

        "tempo_formatado": (
            game.tempo_formatado()
            if game.inicio_partida is not None
            else None
        ),

        "pecas": game.board.quantidade_pecas(),
        "total_pecas": 16,

        "mesa_completa": game.board.completa(),
        "mesa_vazia": game.board.vazia(),

        "tentativas": game.tentativas,
        "resultado": game.resultado_final,

        "mesa": game.board.slots,
    }


# ============================================================
# SISTEMA
# ============================================================

@app.get("/")
def raiz():

    return {
        "sistema": "Quem Mora Onde?",
        "status": "online",
    }


@app.get("/estado")
def obter_estado():

    with medir("GET /estado snapshot"):
        return estado_do_jogo()


# ============================================================
# PARTIDA
# ============================================================

@app.post("/partida/iniciar")
def iniciar_partida():

    if nfc_manager.diagnostico()["nfc_status"] != "pronto":
        return {"sucesso": False, "motivo": "NFC ainda nao esta pronto",
                **estado_do_jogo()}

    sucesso = game.iniciar_partida()

    return {
        "sucesso": sucesso,
        **estado_do_jogo(),
    }


@app.post("/partida/verificar")
def verificar_partida():

    sucesso = game.verificar()

    return {
        "sucesso": sucesso,
        **estado_do_jogo(),
    }


# ============================================================
# DESENVOLVIMENTO - PEÇAS INDIVIDUAIS
# ============================================================

@app.post("/dev/peca/colocar")
def colocar_peca(dados: ColocarPecaRequest):

    sucesso = game.colocar_peca(
        dados.local,
        dados.tipo,
        dados.peca,
    )

    return {
        "sucesso": sucesso,
        **estado_do_jogo(),
    }


@app.post("/dev/peca/retirar")
def retirar_peca(dados: RetirarPecaRequest):

    peca = game.retirar_peca(
        dados.local,
        dados.tipo,
    )

    return {
        "sucesso": peca is not None,
        "peca_retirada": peca,
        **estado_do_jogo(),
    }


# ============================================================
# DESENVOLVIMENTO - SIMULAÇÕES
# ============================================================

@app.post("/dev/montagem/correta")
def montagem_correta():

    sucesso = game.simular_montagem_correta()

    return {
        "sucesso": sucesso,
        **estado_do_jogo(),
    }


@app.post("/dev/montagem/incorreta")
def montagem_incorreta():

    sucesso = game.simular_montagem_incorreta()

    return {
        "sucesso": sucesso,
        **estado_do_jogo(),
    }


@app.post("/dev/retirar-todas")
def retirar_todas():

    sucesso = game.simular_retirada_das_pecas()

    return {
        "sucesso": sucesso,
        **estado_do_jogo(),
    }