import time
from smartcard.System import readers
from smartcard.util import toHexString

ultimo_estado = {}

print("\n=== TESTE MESA INTELIGENTE ===")
print("Pressione CTRL+C para encerrar.\n")

while True:
    lista = readers()

    for i, leitor in enumerate(lista):
        nome = str(leitor)

        try:
            conexao = leitor.createConnection()
            conexao.connect()

            comando_uid = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            dados, sw1, sw2 = conexao.transmit(comando_uid)

            if sw1 == 0x90 and sw2 == 0x00:
                estado = toHexString(dados)
            else:
                estado = None

        except Exception:
            estado = None

        # Só mostra quando alguma coisa mudar
        if ultimo_estado.get(nome) != estado:

            if estado:
                print(f"🟢 LEITOR {i} → PEÇA DETECTADA: {estado}")
            else:
                print(f"⚪ LEITOR {i} → VAZIO")

            ultimo_estado[nome] = estado

    time.sleep(0.25)