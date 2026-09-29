from smartcard.System import readers
from smartcard.Exceptions import NoCardException, CardConnectionException


def formatar_uid(uid):
    return " ".join(f"{byte:02X}" for byte in uid)


leitores = readers()

print("\n==============================")
print("   TESTE NFC - QUEM MORA ONDE")
print("==============================\n")

if not leitores:
    print("❌ Nenhum leitor NFC encontrado.")
    raise SystemExit

print(f"Leitores encontrados: {len(leitores)}\n")

for indice, leitor in enumerate(leitores):
    print(f"[{indice}] {leitor}")

print("\nTentando ler o cartão...\n")

for indice, leitor in enumerate(leitores):

    try:
        conexao = leitor.createConnection()
        conexao.connect()

        # Comando APDU para obter UID
        comando_uid = [
            0xFF,
            0xCA,
            0x00,
            0x00,
            0x00,
        ]

        resposta, sw1, sw2 = conexao.transmit(
            comando_uid
        )

        if sw1 == 0x90 and sw2 == 0x00:

            uid = formatar_uid(resposta)

            print("✅ CARTÃO DETECTADO")
            print(f"Leitor: [{indice}] {leitor}")
            print(f"UID: {uid}")

        else:

            print(
                f"⚠️ Leitor [{indice}] respondeu, "
                f"mas não retornou uma UID válida."
            )

            print(
                f"Status: {sw1:02X} {sw2:02X}"
            )

    except NoCardException:

        print(
            f"⚪ Leitor [{indice}]: "
            f"nenhum cartão presente."
        )

    except CardConnectionException:

        print(
            f"⚠️ Leitor [{indice}]: "
            f"não foi possível conectar ao cartão."
        )

    except Exception as erro:

        print(
            f"❌ Erro no leitor [{indice}]: {erro}"
        )