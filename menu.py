import subprocess
import sys

PORTA = 'COM3'  # Linux: "/dev/ttyACM0" | Mac: "/dev/cu.usbmodemXXXX"


while True:
    try:
        print(f"="*30, "\n           Playlists: \n\n1-The legend of zelda\n2-Jojo\n3-Piratas do Caribe\n\n","="*30)
        usuario = int(input("escolha:"))
        if usuario == 1:
            print("="*30, "\n          Músicas: \n\n1-Songs of storms\n2-Lost woods\n3-Great fairy fountain\n0-voltar\n\n", "="*30)
            musica_zelda= int(input(""))
            if musica_zelda == 1:
                subprocess.run([sys.executable, "song_of_storms.py"], check=True)
            elif musica_zelda ==2:
                subprocess.run([sys.executable, "Lost_woods.py"], check=True)
            elif musica_zelda ==3:
                subprocess.run([sys.executable, "Great fairy Fountain.py"], check=True)
            elif musica_zelda ==0:
                print(f"="*30, "\n           Playlists: \n\n1-The legend of zelda\n2-Jojo\n3-Piratas do Caribe\n4-Steel Ball run\n\n","="*30)

        elif usuario == 2:
            print("="*30, "\n          Músicas: \n\n1-Golden Wind\n2-Steel Ball run\n0-voltar\n\n", "="*30)
            musica_jojo = int(input(""))
            if musica_jojo == 1:
                subprocess.run([sys.executable, "Golden_Wind.py"], check=True)
            elif musica_jojo == 2: 
                subprocess.run([sys.executable, "Steel Ball run.py"], check=True)
            elif musica_jojo == 0:
                print(f"="*30, "\n           Playlists: \n\n1-The legend of zelda\n2-Jojo\n3-Piratas do Caribe\n4-Steel Ball run\n\n","="*30)

        elif usuario == 3:
            subprocess.run([sys.executable, "piratas_do_caribe.py"], check=True) 

        elif usuario == 0:
            print("Tchau, Boiola!")
            break
        else:
            print("Erro: digite 1, 2 ou 3.")
    except ValueError:
        print("Erro: digite um número válido (1, 2 ou 3).")
        
 
 