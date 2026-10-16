import serial
import time

PORTA = 'COM3'  # Linux: "/dev/ttyACM0" | Mac: "/dev/cu.usbmodemXXXX"


# Frequências das notas, em Hz
NOTE_REST = 0

# Notas do Baixo (Graves)
NOTE_C3 = 131
NOTE_D3 = 147
NOTE_E3 = 165
NOTE_F3 = 175
NOTE_FS3= 185
NOTE_G3 = 196
NOTE_GS3= 208
NOTE_A3 = 220
NOTE_AS3= 233
NOTE_B3 = 247

# Notas da Melodia (Agudas)
NOTE_C4 = 262
NOTE_CS4= 277
NOTE_D4 = 294
NOTE_DS4= 311
NOTE_E4 = 330
NOTE_F4 = 349
NOTE_FS4= 370
NOTE_G4 = 392
NOTE_GS4= 415
NOTE_A4 = 440
NOTE_AS4= 466
NOTE_B4 = 494
NOTE_C5 = 523
NOTE_CS5= 554
NOTE_D5 = 587
NOTE_DS5= 622
NOTE_E5 = 659
NOTE_F5 = 698
NOTE_FS5= 740
NOTE_G5 = 784
NOTE_GS5= 831
NOTE_A5 = 880
NOTE_AS5= 932
NOTE_B5 = 988
NOTE_C6 = 1047

# ---------- Oitava ----------
# Buzzer passivo pequeno soa muito fraco abaixo de ~300 Hz, entao o
# arranjo inteiro sobe uma oitava. Multiplicador da frequencia:
#   1 = original | 2 = sobe 1 oitava | 4 = sobe 2 oitavas
# (Se mexer, mude os dois juntos para manter a harmonia.)
MULT_MELODIA = 1
MULT_BAIXO  = 1

# ---------- Andamento (compasso 4/4) ----------
BEAT_MS   = 450               # 1 tempo (seminima) em ms
COLCHEIA  = BEAT_MS / 2       # 1/2 tempo
SEMINIMA  = BEAT_MS           # 1 tempo
MINIMA    = BEAT_MS * 2       # 2 tempos
SEMIBREVE = BEAT_MS * 4       # 4 tempos (compasso inteiro)

# Partitura: [Frequência Melodia, Frequência Baixo, Duração Total em ms]
# Acordes: Lá menor (Am) - Fá (F) - Dó (C) - Sol (G)
partitura = [
    # PARTE 1: arpejo rápido, 4 compassos
    # Am
    [NOTE_A4, NOTE_A3, COLCHEIA], [NOTE_C5, NOTE_A3, COLCHEIA],
    [NOTE_E5, NOTE_A3, COLCHEIA], [NOTE_C5, NOTE_A3, COLCHEIA],
    [NOTE_A4, NOTE_A3, COLCHEIA], [NOTE_C5, NOTE_A3, COLCHEIA],
    [NOTE_E5, NOTE_A3, COLCHEIA], [NOTE_C5, NOTE_A3, COLCHEIA],
    # F
    [NOTE_F4, NOTE_F3, COLCHEIA], [NOTE_A4, NOTE_F3, COLCHEIA],
    [NOTE_C5, NOTE_F3, COLCHEIA], [NOTE_A4, NOTE_F3, COLCHEIA],
    [NOTE_F4, NOTE_F3, COLCHEIA], [NOTE_A4, NOTE_F3, COLCHEIA],
    [NOTE_C5, NOTE_F3, COLCHEIA], [NOTE_A4, NOTE_F3, COLCHEIA],
    # C
    [NOTE_C5, NOTE_C4, COLCHEIA], [NOTE_E5, NOTE_C4, COLCHEIA],
    [NOTE_G5, NOTE_C4, COLCHEIA], [NOTE_E5, NOTE_C4, COLCHEIA],
    [NOTE_C5, NOTE_C4, COLCHEIA], [NOTE_E5, NOTE_C4, COLCHEIA],
    [NOTE_G5, NOTE_C4, COLCHEIA], [NOTE_E5, NOTE_C4, COLCHEIA],
    # G
    [NOTE_G4, NOTE_G3, COLCHEIA], [NOTE_B4, NOTE_G3, COLCHEIA],
    [NOTE_D5, NOTE_G3, COLCHEIA], [NOTE_B4, NOTE_G3, COLCHEIA],
    [NOTE_G4, NOTE_G3, COLCHEIA], [NOTE_B4, NOTE_G3, COLCHEIA],
    [NOTE_D5, NOTE_G3, COLCHEIA], [NOTE_B4, NOTE_G3, COLCHEIA],

    # PARTE 2: melodia lenta em cima dos mesmos acordes
    [NOTE_E5, NOTE_A3, MINIMA], [NOTE_D5, NOTE_A3, SEMINIMA], [NOTE_C5, NOTE_A3, SEMINIMA],   # Am
    [NOTE_C5, NOTE_F3, MINIMA], [NOTE_A4, NOTE_F3, MINIMA],                                   # F
    [NOTE_E5, NOTE_C4, MINIMA], [NOTE_G5, NOTE_C4, MINIMA],                                   # C
    [NOTE_D5, NOTE_G3, MINIMA], [NOTE_B4, NOTE_G3, MINIMA],                                   # G

    # FINAL
    [NOTE_A4, NOTE_A3, SEMIBREVE],
]

print("Conectando ao Arduino...")
arduino = serial.Serial(PORTA, 9600, timeout=5)
time.sleep(2)
print("Conectado! Tocando música...")

for acorde in partitura:
    freq_m = acorde[0]
    freq_b = acorde[1]
    duracao = int(acorde[2])

    comando = f"{freq_m} {freq_b} {duracao}\n"
    arduino.write(comando.encode('utf-8'))

    # Aguarda o Arduino terminar o acorde e responder "OK"
    resposta = arduino.readline()

arduino.close()
print("Fim da música!")