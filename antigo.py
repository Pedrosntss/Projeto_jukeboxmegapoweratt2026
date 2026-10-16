import serial
import time

PORTA = 'COM3'  # Ajuste para a sua porta correta
BAUDRATE = 9600

print("Conectando ao Arduino...")
arduino = serial.Serial(PORTA, BAUDRATE, timeout=2)
time.sleep(2)
print("Conectado! Tocando música com Arpejo 8-bit...")

# Partitura: [Frequência Melodia, Frequência Baixo, Duração Total em ms]
partitura = [
    [523, 131, 400],  # Dó agudo + Dó grave
    [587, 147, 400],  # Ré agudo + Ré grave
    [659, 165, 400],  # Mi agudo + Mi grave
    [698, 175, 500],  # Fá agudo + Fá grave
    [659, 165, 400],  # Mi agudo + Mi grave
    [587, 147, 400],  # Ré agudo + Ré grave
    [523, 131, 800],  # Dó agudo + Dó grave final
]

for acorde in partitura:
    freq_m = acorde[0]
    freq_b = acorde[1]
    duracao = acorde[2]

    # Envia o pacote completo para o Arduino
    comando = f"{freq_m},{freq_b},{duracao}\n"
    arduino.write(comando.encode('utf-8'))

    # Aguarda o Arduino terminar o acorde e responder "OK"
    resposta = ""
    while "OK" not in resposta:
        if arduino.in_waiting > 0:
            resposta = arduino.readline().decode('utf-8').strip()

arduino.close()
print("Fim da música!")