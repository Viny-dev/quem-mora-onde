from smartcard.System import readers
from smartcard.util import toHexString

print("\n=== DIAGNÓSTICO ACR122U ===\n")

lista = readers()

print(f"Leitores PC/SC encontrados: {len(lista)}\n")

for i, leitor in enumerate(lista):
    print("=" * 60)
    print(f"ÍNDICE PC/SC : {i}")
    print(f"NOME         : {leitor}")

    try:
        conexao = leitor.createConnection()
        conexao.connect()

        # ATR do cartão
        print(f"ATR          : {toHexString(conexao.getATR())}")

        # UID do cartão
        dados, sw1, sw2 = conexao.transmit(
            [0xFF, 0xCA, 0x00, 0x00, 0x00]
        )

        if sw1 == 0x90 and sw2 == 0x00:
            print(f"UID CARTÃO   : {toHexString(dados)}")
        else:
            print(f"UID CARTÃO   : erro ({sw1:02X} {sw2:02X})")

        # Firmware do ACR122U
        dados, sw1, sw2 = conexao.transmit(
            [0xFF, 0x00, 0x48, 0x00, 0x00]
        )

        if sw1 == 0x90 and sw2 == 0x00:
            try:
                firmware = bytes(dados).decode("ascii")
            except Exception:
                firmware = toHexString(dados)

            print(f"FIRMWARE     : {firmware}")
        else:
            print(
                f"FIRMWARE     : comando recusado "
                f"({sw1:02X} {sw2:02X})"
            )

    except Exception as erro:
        print("CARTÃO       : não detectado")
        print(f"DETALHE      : {erro}")

print("\n=== FIM DO DIAGNÓSTICO ===")