import subprocess
import sys

PORTA = 'COM3'  # Linux: "/dev/ttyACM0" | Mac: "/dev/cu.usbmodemXXXX"

print(f"="*30, "\n           Playlists: \n\n1-The legend of zelda\n2-Jojo\n3-Piratas do Caribe\n\n","="*30)

try:
    usuario = int(input(""))
    if usuario == 1:
        subprocess.run([sys.executable, "Original  zelda.py"], check=True)
    elif usuario == 2:
        subprocess.run([sys.executable, "Golden_Wind.py"], check=True)
    elif usuario == 3:
        subprocess.run([sys.executable, "piratas_do_caribe.py"], check=True)
    else:
        print("Erro: digite 1, 2 ou 3.")
        raise SystemExit(1)
except ValueError:
    print("Erro: digite um número válido (1, 2 ou 3).")
    raise SystemExit(1)

 