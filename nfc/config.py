"""Configuracao centralizada do primeiro teste fisico."""

CARTOES = {
    "93 64 34 FE": "lucas",
    "13 F9 84 02": "coelho",
    "44 D6 A3 6F": "amarela",
    "C3 52 C1 D9": "livro",
    "76 A8 A5 6F": "ana",
    "63 FF 3F FE": "azul",
    "43 97 67 FE": "cachorro",
    "43 9E BB 3F": "bicicleta",
}

# Identidade fisica: manter leitores nas mesmas portas USB/hub.
LEITORES = {
    "PCIROOT(0)#PCI(1400)#USBROOT(0)#USB(1)#USB(2)": {"local": "arvore", "tipo": "morador"},
    "PCIROOT(0)#PCI(1400)#USBROOT(0)#USB(1)#USB(3)": {"local": "arvore", "tipo": "animal"},
    "PCIROOT(0)#PCI(1400)#USBROOT(0)#USB(1)#USB(1)": {"local": "arvore", "tipo": "cor"},
    "PCIROOT(0)#PCI(1400)#USBROOT(0)#USB(1)#USB(4)": {"local": "arvore", "tipo": "hobby"},
    "PCIROOT(0)#PCI(1400)#USBROOT(0)#USB(9)#USB(1)": {"local": "parquinho", "tipo": "morador"},
    "PCIROOT(0)#PCI(1400)#USBROOT(0)#USB(9)#USB(2)": {"local": "parquinho", "tipo": "cor"},
    "PCIROOT(0)#PCI(1400)#USBROOT(0)#USB(9)#USB(3)": {"local": "parquinho", "tipo": "animal"},
    "PCIROOT(0)#PCI(1400)#USBROOT(0)#USB(9)#USB(4)": {"local": "parquinho", "tipo": "hobby"},
}
APDU_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
INTERVALO = 0.25
