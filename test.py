import serial
import time
import pygame

# Configuração da porta serial (substitua 'COM3' pela porta correta do seu Arduino, ex: '/dev/ttyUSB0' no Linux)
PORTA = 'COM3'

print("Iniciando o cérebro da Jukebox...")

# Inicializa o Pygame Mixer para o som
pygame.mixer.init()

try: 
    # Abre a conexão serial com o Arduino
    arduino = serial.Serial(PORTA, 9600, timeout=1)
    time.sleep(2) 
    print(f"Conectado ao arduino na porta {PORTA}. Aguardando comandos...")

    while True:
        # Verifica se chegou alguma informação do Arduino
        if arduino.in_waiting > 0:
            # Lê a linha enviada pelo Arduino e remove espaços/quebras de linha
            comando = arduino.readline().decode('utf-8').strip()

            print(f"Comando recebido do Arduino: {comando}")

            if comando == '1': 
                print("Tocando a musica 1")
                pygame.mixer.music.load("musica mp3")

            elif comando == 2:
                print("Parando a Musica...")
                pygame.mixer.music.stop()

    # Pequena pausa para não sobrecarregar o processador do computador
        time.sleep(0.1)

except serial.SerialException:
    print(f"Erro: Não foi possível conectar na porta {PORTA}. Verifique se o Monitor Serial da Arduino IDE está fechado.")
except KeyboardInterrupt:
    print("\nEncerrando a Jukebox...")
    pygame.mixer.quit()
