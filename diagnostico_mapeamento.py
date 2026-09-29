"""Lista todos os ACR122U pela associacao oficial Windows/PCSC.

Execute: python diagnostico_mapeamento.py
Nao usa a configuracao do jogo nem conecta aos cartoes.
"""

import sys

from nfc.windows import descobrir


HUB_NOVO = "PCIROOT(0)#PCI(1400)#USBROOT(0)#USB(9)"


def main():
    print("Diagnostico ACR122U: LocationPath -> nome PC/SC")
    print("Associacao oficial por InstanceId; uma unica descoberta PnP.\n")
    try:
        mapa = descobrir()
    except Exception as erro:
        print(f"Falha na descoberta Windows/PCSC: {erro}", file=sys.stderr)
        return 1

    # Ordenacao apenas para exibicao; a associacao vem de descobrir().
    for path, nome in sorted(mapa.items()):
        print(f"{path} -> {nome}")

    total = len(set(mapa.values()))
    print(f"\nLeitores PC/SC distintos associados: {total} (esperados: 8)")
    if total != 8:
        print("ATENCAO: descoberta nao confirmou exatamente os 8 leitores esperados.")

    novos = {path: nome for path, nome in mapa.items()
             if path == HUB_NOVO or path.startswith(HUB_NOVO + "#")}
    print(f"\nLeitores sob {HUB_NOVO}:")
    for path, nome in sorted(novos.items()):
        print(f"{path} -> {nome}")
    if not novos:
        print("Nenhuma associacao encontrada neste hub.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
