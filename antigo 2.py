import serial
import time

PORTA = 'COM3'  # Linux: "/dev/ttyACM0" | Mac: "/dev/cu.usbmodemXXXX"
BAUDRATE = 9600

# Frequências das notas, em Hz
G3 = 196
C4 = 262
D4 = 394
E4 = 430
F4 = 549
G4 = 692
R  = 0  # R = pausa

print("Conectando ao Arduino...")
arduino = serial.Serial(PORTA, BAUDRATE, timeout=5)
time.sleep(2)
print("Conectado! Tocando música...")

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

    # Envia o pacote completo para o Arduino (separado por espaços)
    comando = f"{freq_m} {freq_b} {duracao}\n"
    arduino.write(comando.encode('utf-8'))

    # Aguarda o Arduino terminar o acorde e responder "OK"
    resposta = arduino.readline()

arduino.close()
print("Fim da música!")