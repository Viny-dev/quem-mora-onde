"""Configuracao centralizada do primeiro teste fisico."""

CARTOES = {
    "93 64 34 FE": "lucas",
    "13 F9 84 02": "coelho",
}

# Identidade fisica: manter leitores nas mesmas portas USB/hub.
LEITORES = {
    "PCIROOT(0)#PCI(1400)#USBROOT(0)#USB(1)#USB(2)": {"local": "arvore", "tipo": "morador"},
    "PCIROOT(0)#PCI(1400)#USBROOT(0)#USB(1)#USB(3)": {"local": "arvore", "tipo": "animal"},
}
APDU_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
INTERVALO = 0.25
