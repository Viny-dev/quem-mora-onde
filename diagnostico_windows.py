import subprocess
from smartcard.System import readers
from smartcard.util import toHexString


def executar_powershell(comando):
    resultado = subprocess.run(
        ["powershell", "-NoProfile", "-Command", comando],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    return resultado.stdout.strip()


print("\n" + "=" * 70)
print("DIAGNÓSTICO PC/SC")
print("=" * 70)

lista = readers()

for i, leitor in enumerate(lista):
    print(f"\nPC/SC {i}")
    print(f"Nome: {leitor}")

    try:
        conexao = leitor.createConnection()
        conexao.connect()

        dados, sw1, sw2 = conexao.transmit(
            [0xFF, 0xCA, 0x00, 0x00, 0x00]
        )

        if sw1 == 0x90 and sw2 == 0x00:
            print(f"UID : {toHexString(dados)}")
        else:
            print("UID : erro")

    except Exception as erro:
        print(f"Cartão: não detectado ({erro})")


print("\n" + "=" * 70)
print("DISPOSITIVOS USB FÍSICOS")
print("=" * 70)

comando_usb = r'''
$readers = Get-PnpDevice -PresentOnly |
    Where-Object {
        $_.Class -eq "SmartCardReader" -and
        $_.FriendlyName -eq "ACR122 Smart Card Reader"
    }

foreach ($r in $readers) {

    $location = Get-PnpDeviceProperty `
        -InstanceId $r.InstanceId `
        -KeyName "DEVPKEY_Device_LocationInfo"

    $path = Get-PnpDeviceProperty `
        -InstanceId $r.InstanceId `
        -KeyName "DEVPKEY_Device_LocationPaths"

    $relation = Get-PnpDeviceProperty `
        -InstanceId $r.InstanceId `
        -KeyName "DEVPKEY_Device_BusRelations"

    Write-Output "DEVICE_START"
    Write-Output ("INSTANCE=" + $r.InstanceId)
    Write-Output ("LOCATION=" + $location.Data)
    Write-Output ("PATH=" + ($path.Data -join ";"))
    Write-Output ("RELATION=" + ($relation.Data -join ";"))
    Write-Output "DEVICE_END"
}
'''

saida = executar_powershell(comando_usb)

print(saida)

print("\n" + "=" * 70)
print("SMART CARD FILTERS ATIVOS")
print("=" * 70)

comando_filter = r'''
Get-PnpDevice -PresentOnly |
    Where-Object {
        $_.Class -eq "SmartCardFilter"
    } |
    ForEach-Object {
        Write-Output (
            $_.FriendlyName + " | " + $_.InstanceId
        )
    }
'''

print(executar_powershell(comando_filter))

print("\n" + "=" * 70)
print("FIM DO DIAGNÓSTICO")
print("=" * 70)