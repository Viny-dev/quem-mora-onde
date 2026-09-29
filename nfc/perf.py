"""Instrumentacao temporaria: NFC_PERF=0 desativa; somente >100 ms."""
import logging
import os
from contextlib import contextmanager
from time import perf_counter

logger = logging.getLogger("uvicorn.error")
ATIVO = os.getenv("NFC_PERF", "1") != "0"


def registrar(operacao, segundos, leitor=None):
    if ATIVO and segundos > 0.1:
        logger.warning("NFC PERF: %s = %.1f ms%s", operacao, segundos * 1000,
                       f" [{leitor}]" if leitor else "")


@contextmanager
def medir(operacao, leitor=None):
    inicio = perf_counter()
    try:
        yield
    finally:
        registrar(operacao, perf_counter() - inicio, leitor)
