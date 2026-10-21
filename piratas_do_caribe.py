import serial
import time

PORTA = 'COM3'  # Linux: "/dev/ttyACM0" | Mac: "/dev/cu.usbmodemXXXX"

# ======================================================================
# Pirates of the Caribbean - He's a Pirate (versao para piano)
# Buzzer 1 = mao direita (melodia) | Buzzer 2 = mao esquerda (baixo)
# Re menor, compasso 3/4, seminima = 150 BPM
# Ordem: anacruse + tema (c. 2-15) + casa 1 (c. 16-17) + tema de novo
#        + casa 2 e ponte (c. 18-26) + parte B + parte C + final (c. 67)
# ======================================================================


# Frequências das notas, em Hz
NOTE_REST = 0

# Notas do Baixo (Graves)
NOTE_F2 = 87
NOTE_G2 = 98
NOTE_A2 = 110
NOTE_AS2= 117
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
# arranjo inteiro sobe duas oitavas (o baixo desce ate Fa2 = 87 Hz,
# grave demais para um buzzer). Multiplicador da frequencia:
#   1 = original | 2 = sobe 1 oitava | 4 = sobe 2 oitavas
# (Se mexer, mude os dois juntos para manter a harmonia.)
MULT_MELODIA = 4
MULT_BAIXO  = 4

# ---------- Andamento (compasso 3/4) ----------
# Para deixar a musica mais rapida/lenta, mexa so no BEAT_MS.
BEAT_MS    = 400              # 1 tempo (seminima) em ms -> 150 BPM
COLCHEIA   = (BEAT_MS / 2)    # 1/2 tempo
SEMINIMA   = (BEAT_MS)        # 1 tempo
SEMINIMA_P = (BEAT_MS * 1.5)  # 1,5 tempo (seminima pontuada)
MINIMA     = (BEAT_MS * 2)    # 2 tempos
MINIMA_C   = (BEAT_MS * 2.5)  # 2,5 tempos (minima + colcheia)
MINIMA_P   = (BEAT_MS * 3)    # 3 tempos (compasso inteiro)

# Silencio entre as notas: 25% da duracao, mas no maximo GAP_MAX_MS
# (evita "buracos" enormes no meio das notas longas)
GAP_RATIO = 0.25
GAP_MAX_MS = 60


# Partitura - Buzzer 1 (Melodia)
melodyNotes = (
  # 1. ANACRUSE (compasso 1)
  NOTE_A3, NOTE_C4,                               # compasso 1

  # 2. TEMA (A) (compassos 2 a 15)
  NOTE_D4, NOTE_D4, NOTE_D4, NOTE_E4,             # compasso 2
  NOTE_F4, NOTE_F4, NOTE_F4, NOTE_G4,             # compasso 3
  NOTE_E4, NOTE_E4, NOTE_D4, NOTE_C4,             # compasso 4
  NOTE_C4, NOTE_D4, NOTE_A3, NOTE_C4,             # compasso 5
  NOTE_D4, NOTE_D4, NOTE_D4, NOTE_E4,             # compasso 6
  NOTE_F4, NOTE_F4, NOTE_F4, NOTE_G4,             # compasso 7
  NOTE_E4, NOTE_E4, NOTE_D4, NOTE_C4,             # compasso 8
  NOTE_D4, NOTE_REST, NOTE_A3, NOTE_C4,           # compasso 9
  NOTE_D4, NOTE_D4, NOTE_D4, NOTE_F4,             # compasso 10
  NOTE_G4, NOTE_G4, NOTE_G4, NOTE_A4,             # compasso 11
  NOTE_AS4, NOTE_AS4, NOTE_A4, NOTE_G4,           # compasso 12
  NOTE_A4, NOTE_D4, NOTE_D4, NOTE_E4,             # compasso 13
  NOTE_F4, NOTE_F4, NOTE_G4,                      # compasso 14
  NOTE_A4, NOTE_D4, NOTE_D4, NOTE_F4,             # compasso 15

  # 3. CASA 1 (compassos 16 e 17, volta ao compasso 2)
  NOTE_E4, NOTE_E4, NOTE_F4, NOTE_D4,             # compasso 16
  NOTE_E4, NOTE_REST, NOTE_A3, NOTE_C4,           # compasso 17

  # 4. TEMA (A - Repeticao) (compassos 2 a 15)
  NOTE_D4, NOTE_D4, NOTE_D4, NOTE_E4,             # compasso 2
  NOTE_F4, NOTE_F4, NOTE_F4, NOTE_G4,             # compasso 3
  NOTE_E4, NOTE_E4, NOTE_D4, NOTE_C4,             # compasso 4
  NOTE_C4, NOTE_D4, NOTE_A3, NOTE_C4,             # compasso 5
  NOTE_D4, NOTE_D4, NOTE_D4, NOTE_E4,             # compasso 6
  NOTE_F4, NOTE_F4, NOTE_F4, NOTE_G4,             # compasso 7
  NOTE_E4, NOTE_E4, NOTE_D4, NOTE_C4,             # compasso 8
  NOTE_D4, NOTE_REST, NOTE_A3, NOTE_C4,           # compasso 9
  NOTE_D4, NOTE_D4, NOTE_D4, NOTE_F4,             # compasso 10
  NOTE_G4, NOTE_G4, NOTE_G4, NOTE_A4,             # compasso 11
  NOTE_AS4, NOTE_AS4, NOTE_A4, NOTE_G4,           # compasso 12
  NOTE_A4, NOTE_D4, NOTE_D4, NOTE_E4,             # compasso 13
  NOTE_F4, NOTE_F4, NOTE_G4,                      # compasso 14
  NOTE_A4, NOTE_D4, NOTE_D4, NOTE_F4,             # compasso 15

  # 5. CASA 2 e PONTE (compassos 18 a 26)
  NOTE_E4, NOTE_E4, NOTE_D4, NOTE_CS4,            # compasso 18
  NOTE_D4, NOTE_D4, NOTE_E4,                      # compasso 19
  NOTE_F4, NOTE_F4, NOTE_G4,                      # compasso 20
  NOTE_A4, NOTE_F4, NOTE_REST, NOTE_F4, NOTE_D4,  # compasso 21
  NOTE_A3, NOTE_REST,                             # compasso 22
  NOTE_AS4, NOTE_REST, NOTE_G4, NOTE_D4,          # compasso 23
  NOTE_AS3, NOTE_REST,                            # compasso 24
  NOTE_E4, NOTE_E4, NOTE_D4,                      # compasso 25
  NOTE_CS4, NOTE_REST, NOTE_F4, NOTE_G4,          # compasso 26

  # 6. PARTE B (compassos 27 a 34)
  NOTE_A4, NOTE_A4, NOTE_A4,                      # compasso 27
  NOTE_AS4, NOTE_A4, NOTE_REST,                   # compasso 28
  NOTE_G4, NOTE_G4, NOTE_G4,                      # compasso 29
  NOTE_G4, NOTE_A4, NOTE_REST,                    # compasso 30
  NOTE_A4, NOTE_A4, NOTE_A4,                      # compasso 31
  NOTE_AS4, NOTE_A4, NOTE_REST,                   # compasso 32
  NOTE_G4, NOTE_F4, NOTE_E4,                      # compasso 33
  NOTE_D4, NOTE_REST, NOTE_D4, NOTE_E4,           # compasso 34

  # 7. PARTE C (compassos 35 a 51)
  NOTE_F4, NOTE_G4, NOTE_A4,                      # compasso 35
  NOTE_G4, NOTE_F4, NOTE_E4,                      # compasso 36
  NOTE_F4, NOTE_G4, NOTE_A4,                      # compasso 37
  NOTE_G4, NOTE_F4, NOTE_G4,                      # compasso 38
  NOTE_A4, NOTE_G4, NOTE_F4,                      # compasso 39
  NOTE_E4, NOTE_F4, NOTE_E4,                      # compasso 40
  NOTE_D4, NOTE_E4, NOTE_CS4,                     # compasso 41
  NOTE_D4, NOTE_REST, NOTE_D4, NOTE_E4,           # compasso 42
  NOTE_F4, NOTE_REST, NOTE_E4, NOTE_F4,           # compasso 43
  NOTE_G4, NOTE_F4, NOTE_G4,                      # compasso 44
  NOTE_A4, NOTE_G4, NOTE_F4,                      # compasso 45
  NOTE_D4, NOTE_REST, NOTE_D4, NOTE_E4,           # compasso 46
  NOTE_F4, NOTE_G4, NOTE_A4,                      # compasso 47
  NOTE_AS4, NOTE_D4, NOTE_G4,                     # compasso 48
  NOTE_F4, NOTE_REST, NOTE_G4, NOTE_E4,           # compasso 49
  NOTE_D4, NOTE_REST, NOTE_E4, NOTE_CS4,          # compasso 50
  NOTE_D4, NOTE_REST, NOTE_A3, NOTE_C4,           # compasso 51

  # 8. FINAL - volta o tema (compassos 52 a 67, ultima nota alongada)
  NOTE_D4, NOTE_D4, NOTE_D4, NOTE_E4,             # compasso 52
  NOTE_F4, NOTE_F4, NOTE_F4, NOTE_G4,             # compasso 53
  NOTE_E4, NOTE_E4, NOTE_D4, NOTE_C4,             # compasso 54
  NOTE_C4, NOTE_D4, NOTE_A3, NOTE_C4,             # compasso 55
  NOTE_D4, NOTE_D4, NOTE_D4, NOTE_E4,             # compasso 56
  NOTE_F4, NOTE_F4, NOTE_F4, NOTE_G4,             # compasso 57
  NOTE_E4, NOTE_E4, NOTE_D4, NOTE_C4,             # compasso 58
  NOTE_D4, NOTE_REST, NOTE_A3, NOTE_C4,           # compasso 59
  NOTE_D4, NOTE_D4, NOTE_D4, NOTE_F4,             # compasso 60
  NOTE_G4, NOTE_G4, NOTE_G4, NOTE_A4,             # compasso 61
  NOTE_AS4, NOTE_AS4, NOTE_A4, NOTE_G4,           # compasso 62
  NOTE_A4, NOTE_D4, NOTE_D4, NOTE_E4,             # compasso 63
  NOTE_F4, NOTE_F4, NOTE_G4,                      # compasso 64
  NOTE_A4, NOTE_D4, NOTE_D4, NOTE_F4,             # compasso 65
  NOTE_E4, NOTE_E4, NOTE_D4, NOTE_CS4,            # compasso 66
  NOTE_D4                                         # compasso 67
)

# Partitura - Buzzer 2 (Baixo)
bassNotes = (
  # 1. ANACRUSE (compasso 1)
  NOTE_REST, NOTE_REST,                         # compasso 1

  # 2. TEMA (A) (compassos 2 a 15)
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 2
  NOTE_AS2, NOTE_AS2, NOTE_AS2, NOTE_AS2,       # compasso 3
  NOTE_A2, NOTE_A2, NOTE_A2, NOTE_A2,           # compasso 4
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 5
  NOTE_AS2, NOTE_AS2, NOTE_AS2, NOTE_AS2,       # compasso 6
  NOTE_F2, NOTE_F2, NOTE_F2, NOTE_F2,           # compasso 7
  NOTE_C3, NOTE_C3, NOTE_C3, NOTE_C3,           # compasso 8
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 9
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 10
  NOTE_AS2, NOTE_AS2, NOTE_AS2, NOTE_AS2,       # compasso 11
  NOTE_G2, NOTE_G2, NOTE_G2, NOTE_G2,           # compasso 12
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 13
  NOTE_AS2, NOTE_AS2, NOTE_AS2,                 # compasso 14
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 15

  # 3. CASA 1 (compassos 16 e 17, volta ao compasso 2)
  NOTE_A2, NOTE_A2, NOTE_A2, NOTE_A2,           # compasso 16
  NOTE_A2, NOTE_A2, NOTE_REST, NOTE_REST,       # compasso 17

  # 4. TEMA (A - Repeticao) (compassos 2 a 15)
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 2
  NOTE_AS2, NOTE_AS2, NOTE_AS2, NOTE_AS2,       # compasso 3
  NOTE_A2, NOTE_A2, NOTE_A2, NOTE_A2,           # compasso 4
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 5
  NOTE_AS2, NOTE_AS2, NOTE_AS2, NOTE_AS2,       # compasso 6
  NOTE_F2, NOTE_F2, NOTE_F2, NOTE_F2,           # compasso 7
  NOTE_C3, NOTE_C3, NOTE_C3, NOTE_C3,           # compasso 8
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 9
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 10
  NOTE_AS2, NOTE_AS2, NOTE_AS2, NOTE_AS2,       # compasso 11
  NOTE_G2, NOTE_G2, NOTE_G2, NOTE_G2,           # compasso 12
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 13
  NOTE_AS2, NOTE_AS2, NOTE_AS2,                 # compasso 14
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 15

  # 5. CASA 2 e PONTE (compassos 18 a 26)
  NOTE_A2, NOTE_A2, NOTE_A2, NOTE_A2,           # compasso 18
  NOTE_D3, NOTE_D3, NOTE_D3,                    # compasso 19
  NOTE_D3, NOTE_D3, NOTE_D3,                    # compasso 20
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,  # compasso 21
  NOTE_D3, NOTE_D3,                             # compasso 22
  NOTE_G2, NOTE_G2, NOTE_G2, NOTE_G2,           # compasso 23
  NOTE_G2, NOTE_G2,                             # compasso 24
  NOTE_A2, NOTE_A2, NOTE_A2,                    # compasso 25
  NOTE_A2, NOTE_A2, NOTE_A2, NOTE_A2,           # compasso 26

  # 6. PARTE B (compassos 27 a 34)
  NOTE_D3, NOTE_D3, NOTE_D3,                    # compasso 27
  NOTE_D3, NOTE_D3, NOTE_D3,                    # compasso 28
  NOTE_C3, NOTE_C3, NOTE_C3,                    # compasso 29
  NOTE_F2, NOTE_F2, NOTE_F2,                    # compasso 30
  NOTE_D3, NOTE_D3, NOTE_D3,                    # compasso 31
  NOTE_D3, NOTE_D3, NOTE_D3,                    # compasso 32
  NOTE_A2, NOTE_A2, NOTE_A2,                    # compasso 33
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 34

  # 7. PARTE C (compassos 35 a 51)
  NOTE_D3, NOTE_D3, NOTE_D3,                    # compasso 35
  NOTE_C3, NOTE_C3, NOTE_C3,                    # compasso 36
  NOTE_F2, NOTE_F2, NOTE_F2,                    # compasso 37
  NOTE_C3, NOTE_C3, NOTE_C3,                    # compasso 38
  NOTE_F2, NOTE_F2, NOTE_F2,                    # compasso 39
  NOTE_A2, NOTE_A2, NOTE_A2,                    # compasso 40
  NOTE_D3, NOTE_D3, NOTE_D3,                    # compasso 41
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 42
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 43
  NOTE_C3, NOTE_C3, NOTE_C3,                    # compasso 44
  NOTE_F2, NOTE_F2, NOTE_F2,                    # compasso 45
  NOTE_AS2, NOTE_AS2, NOTE_AS2, NOTE_AS2,       # compasso 46
  NOTE_D3, NOTE_D3, NOTE_D3,                    # compasso 47
  NOTE_G2, NOTE_G2, NOTE_G2,                    # compasso 48
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 49
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 50
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 51

  # 8. FINAL - volta o tema (compassos 52 a 67, ultima nota alongada)
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 52
  NOTE_AS2, NOTE_AS2, NOTE_AS2, NOTE_AS2,       # compasso 53
  NOTE_A2, NOTE_A2, NOTE_A2, NOTE_A2,           # compasso 54
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 55
  NOTE_AS2, NOTE_AS2, NOTE_AS2, NOTE_AS2,       # compasso 56
  NOTE_F2, NOTE_F2, NOTE_F2, NOTE_F2,           # compasso 57
  NOTE_C3, NOTE_C3, NOTE_C3, NOTE_C3,           # compasso 58
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 59
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 60
  NOTE_AS2, NOTE_AS2, NOTE_AS2, NOTE_AS2,       # compasso 61
  NOTE_G2, NOTE_G2, NOTE_G2, NOTE_G2,           # compasso 62
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 63
  NOTE_AS2, NOTE_AS2, NOTE_AS2,                 # compasso 64
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,           # compasso 65
  NOTE_A2, NOTE_A2, NOTE_A2, NOTE_A2,           # compasso 66
  NOTE_D3                                       # compasso 67
)

# Duracoes (ms)
noteDurations = (
  # 1. ANACRUSE (compasso 1)
  COLCHEIA, COLCHEIA,                                # compasso 1

  # 2. TEMA (A) (compassos 2 a 15)
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 2
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 3
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 4
  COLCHEIA, SEMINIMA_P, COLCHEIA, COLCHEIA,          # compasso 5
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 6
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 7
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 8
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 9
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 10
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 11
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 12
  COLCHEIA, SEMINIMA_P, COLCHEIA, COLCHEIA,          # compasso 13
  SEMINIMA, SEMINIMA, SEMINIMA,                      # compasso 14
  COLCHEIA, SEMINIMA_P, COLCHEIA, COLCHEIA,          # compasso 15

  # 3. CASA 1 (compassos 16 e 17, volta ao compasso 2)
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 16
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 17

  # 4. TEMA (A - Repeticao) (compassos 2 a 15)
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 2
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 3
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 4
  COLCHEIA, SEMINIMA_P, COLCHEIA, COLCHEIA,          # compasso 5
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 6
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 7
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 8
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 9
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 10
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 11
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 12
  COLCHEIA, SEMINIMA_P, COLCHEIA, COLCHEIA,          # compasso 13
  SEMINIMA, SEMINIMA, SEMINIMA,                      # compasso 14
  COLCHEIA, SEMINIMA_P, COLCHEIA, COLCHEIA,          # compasso 15

  # 5. CASA 2 e PONTE (compassos 18 a 26)
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 18
  SEMINIMA, SEMINIMA, SEMINIMA,                      # compasso 19
  SEMINIMA, SEMINIMA, SEMINIMA,                      # compasso 20
  COLCHEIA, COLCHEIA, SEMINIMA, COLCHEIA, COLCHEIA,  # compasso 21
  COLCHEIA, MINIMA_C,                                # compasso 22
  COLCHEIA, SEMINIMA_P, COLCHEIA, COLCHEIA,          # compasso 23
  COLCHEIA, MINIMA_C,                                # compasso 24
  COLCHEIA, SEMINIMA, SEMINIMA_P,                    # compasso 25
  SEMINIMA_P, COLCHEIA, COLCHEIA, COLCHEIA,          # compasso 26

  # 6. PARTE B (compassos 27 a 34)
  SEMINIMA, SEMINIMA, SEMINIMA,                      # compasso 27
  COLCHEIA, COLCHEIA, MINIMA,                        # compasso 28
  SEMINIMA, SEMINIMA, SEMINIMA,                      # compasso 29
  COLCHEIA, SEMINIMA, SEMINIMA_P,                    # compasso 30
  SEMINIMA, SEMINIMA, SEMINIMA,                      # compasso 31
  COLCHEIA, COLCHEIA, MINIMA,                        # compasso 32
  SEMINIMA, SEMINIMA, SEMINIMA,                      # compasso 33
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 34

  # 7. PARTE C (compassos 35 a 51)
  MINIMA, COLCHEIA, COLCHEIA,                        # compasso 35
  SEMINIMA, SEMINIMA, SEMINIMA,                      # compasso 36
  SEMINIMA, SEMINIMA, SEMINIMA,                      # compasso 37
  MINIMA, COLCHEIA, COLCHEIA,                        # compasso 38
  MINIMA, COLCHEIA, COLCHEIA,                        # compasso 39
  SEMINIMA, SEMINIMA, SEMINIMA,                      # compasso 40
  MINIMA, COLCHEIA, COLCHEIA,                        # compasso 41
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 42
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 43
  SEMINIMA, SEMINIMA, SEMINIMA,                      # compasso 44
  SEMINIMA, SEMINIMA, SEMINIMA,                      # compasso 45
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 46
  SEMINIMA, SEMINIMA, SEMINIMA,                      # compasso 47
  SEMINIMA, SEMINIMA, SEMINIMA,                      # compasso 48
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 49
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 50
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 51

  # 8. FINAL - volta o tema (compassos 52 a 67, ultima nota alongada)
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 52
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 53
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 54
  COLCHEIA, SEMINIMA_P, COLCHEIA, COLCHEIA,          # compasso 55
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 56
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 57
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 58
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 59
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 60
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 61
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 62
  COLCHEIA, SEMINIMA_P, COLCHEIA, COLCHEIA,          # compasso 63
  SEMINIMA, SEMINIMA, SEMINIMA,                      # compasso 64
  COLCHEIA, SEMINIMA_P, COLCHEIA, COLCHEIA,          # compasso 65
  SEMINIMA, SEMINIMA, COLCHEIA, COLCHEIA,            # compasso 66
  MINIMA_P                                           # compasso 67
)

print("Conectando ao Arduino...")
arduino = serial.Serial(PORTA, 9600, timeout=5)
time.sleep(2)
print("Conectado! Tocando música...")

# Partitura: [Frequência Melodia, Frequência Baixo, Duração Total em ms]

for i in range(len(melodyNotes)):
    freq_m = melodyNotes[i] * MULT_MELODIA
    freq_b = bassNotes[i] * MULT_BAIXO
    duracao = int(noteDurations[i])

    # Envia o pacote completo para o Arduino (separado por espaços)
    comando = f"{freq_m} {freq_b} {duracao}\n"
    arduino.write(comando.encode('utf-8'))

    # Aguarda o Arduino terminar o acorde e responder "OK"
    resposta = arduino.readline()

arduino.close()
print("Fim da música!")