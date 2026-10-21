import serial
import time

PORTA = 'COM3'  # Linux: "/dev/ttyACM0" | Mac: "/dev/cu.usbmodemXXXX"

# ======================================================================
# JoJo's Bizarre Adventure: Golden Wind - Giorno's Theme
# Buzzer 1 = mao direita (melodia) | Buzzer 2 = mao esquerda (baixo)
# ======================================================================


# Frequencias das notas, em Hz
NOTE_REST = 0

# Notas do Baixo (Graves)
NOTE_FS2 = 93
NOTE_GS2 = 104
NOTE_A2  = 110
NOTE_B2  = 123
NOTE_CS3 = 139
NOTE_D3  = 147
NOTE_E3  = 165
NOTE_F3  = 175

# Notas da Melodia (Agudas)
NOTE_FS4 = 370
NOTE_A4  = 440
NOTE_B4  = 494
NOTE_CS5 = 554
NOTE_D5  = 587
NOTE_E5  = 659
NOTE_F5  = 698
NOTE_FS5 = 740
NOTE_G5  = 784
NOTE_A5  = 880
NOTE_AS5 = 932
NOTE_B5  = 988
NOTE_CS6 = 1109
NOTE_D6  = 1175
NOTE_E6  = 1319

# ---------- Oitava ----------
# Multiplicador da frequencia:
#   1 = original | 2 = sobe 1 oitava | 4 = sobe 2 oitavas
# O baixo do tema e grave (Fa#2 = 93 Hz); se o buzzer 2 ficar fraco, ponha 4.
# (Na introducao as duas maos tocam o mesmo riff, com 1 oitava de diferenca;
# por isso as notas da intro ja estao escritas na oitava certa de cada voz.)
MULT_MELODIA = 1
MULT_BAIXO   = 2

# ---------- Andamento (compasso 4/4, seminima = 130 BPM) ----------
# Para deixar a musica mais rapida/lenta, mexa so no BPM.
BPM      = 130
BEAT_MS  = 60000 / BPM             # 1 tempo (seminima) em ms
SEMICOLCHEIA = (BEAT_MS / 4)       # 1/4 de tempo
COLCHEIA     = (BEAT_MS / 2)       # 1/2 tempo
COLCHEIA_P   = (BEAT_MS * 0.75)    # 3/4 de tempo (colcheia pontuada)
SEMINIMA     = (BEAT_MS)           # 1 tempo
SEMINIMA_P   = (BEAT_MS * 1.5)     # 1 tempo e meio
MINIMA       = (BEAT_MS * 2)       # 2 tempos
MINIMA_P     = (BEAT_MS * 3)       # 3 tempos

# Silencio curto entre duas notas iguais seguidas (senao elas "grudam").
# As notas staccato da intro ja estao escritas como nota curta + pausa.
GAP_MS = 30


# Partitura - Buzzer 1 (Melodia)
melodyNotes = (
  # 1. INTRO (compassos 1-8: o riff, as duas maos tocam)
  NOTE_B4, NOTE_REST, NOTE_B4, NOTE_REST, NOTE_B4, NOTE_A4,                             # compasso 1
  NOTE_REST, NOTE_B4, NOTE_REST, NOTE_D5, NOTE_REST, NOTE_B4,
  NOTE_REST, NOTE_FS4, NOTE_A4,
  NOTE_B4, NOTE_REST, NOTE_B4, NOTE_REST, NOTE_B4, NOTE_A4,                             # compasso 2
  NOTE_REST, NOTE_B4, NOTE_REST, NOTE_F5, NOTE_REST, NOTE_E5,
  NOTE_REST, NOTE_D5, NOTE_A4,
  NOTE_B4, NOTE_REST, NOTE_B4, NOTE_REST, NOTE_B4, NOTE_A4,                             # compasso 3
  NOTE_REST, NOTE_B4, NOTE_REST, NOTE_D5, NOTE_REST, NOTE_B4,
  NOTE_REST, NOTE_FS4, NOTE_A4,
  NOTE_B4, NOTE_REST, NOTE_B4, NOTE_REST, NOTE_B4, NOTE_A4,                             # compasso 4
  NOTE_REST, NOTE_B4, NOTE_REST, NOTE_F5, NOTE_REST, NOTE_E5,
  NOTE_REST, NOTE_B4, NOTE_A4,
  NOTE_B4, NOTE_REST, NOTE_B4, NOTE_REST, NOTE_B4, NOTE_A4,                             # compasso 5
  NOTE_REST, NOTE_B4, NOTE_REST, NOTE_D5, NOTE_REST, NOTE_B4,
  NOTE_REST, NOTE_FS4, NOTE_A4,
  NOTE_B4, NOTE_REST, NOTE_B4, NOTE_REST, NOTE_B4, NOTE_A4,                             # compasso 6
  NOTE_REST, NOTE_B4, NOTE_REST, NOTE_F5, NOTE_REST, NOTE_E5,
  NOTE_REST, NOTE_D5, NOTE_A4,
  NOTE_B4, NOTE_REST, NOTE_B4, NOTE_REST, NOTE_B4, NOTE_A4,                             # compasso 7
  NOTE_REST, NOTE_B4, NOTE_REST, NOTE_D5, NOTE_REST, NOTE_B4,
  NOTE_REST, NOTE_FS4, NOTE_A4,
  NOTE_B4, NOTE_REST, NOTE_B4, NOTE_REST, NOTE_B4, NOTE_REST,                           # compasso 8
  NOTE_A4, NOTE_B4, NOTE_REST,

  # 2. TEMA (compassos 9-24)
  NOTE_FS5, NOTE_F5, NOTE_REST, NOTE_D5, NOTE_E5,                                       # compasso 9
  NOTE_F5, NOTE_E5, NOTE_D5, NOTE_CS5, NOTE_D5, NOTE_E5,                                # compasso 10
  NOTE_FS5, NOTE_B5, NOTE_B4, NOTE_CS5,                                                 # compasso 11
  NOTE_D5, NOTE_E5, NOTE_D5, NOTE_CS5, NOTE_A5, NOTE_G5,                                # compasso 12
  NOTE_FS5, NOTE_F5, NOTE_REST, NOTE_D5, NOTE_E5,                                       # compasso 13
  NOTE_F5, NOTE_E5, NOTE_D5, NOTE_CS5, NOTE_D5, NOTE_E5,                                # compasso 14
  NOTE_FS5, NOTE_B5, NOTE_REST, NOTE_B5, NOTE_CS6,                                      # compasso 15
  NOTE_D6, NOTE_E6, NOTE_G5, NOTE_FS5, NOTE_D6, NOTE_E6,                                # compasso 16
  NOTE_FS5, NOTE_F5, NOTE_REST, NOTE_D5, NOTE_E5,                                       # compasso 17
  NOTE_F5, NOTE_E5, NOTE_D5, NOTE_CS5, NOTE_D5, NOTE_E5,                                # compasso 18
  NOTE_FS5, NOTE_B5, NOTE_B4, NOTE_CS5,                                                 # compasso 19
  NOTE_D5, NOTE_E5, NOTE_D5, NOTE_CS5, NOTE_A5, NOTE_G5,                                # compasso 20
  NOTE_FS5, NOTE_F5, NOTE_REST, NOTE_D5, NOTE_E5,                                       # compasso 21
  NOTE_FS5, NOTE_B5, NOTE_B4, NOTE_CS5,                                                 # compasso 22
  NOTE_D5, NOTE_G5, NOTE_FS5, NOTE_F5, NOTE_D6, NOTE_AS5,                               # compasso 23
  NOTE_B5, NOTE_REST                                                                    # compasso 24
)

# Partitura - Buzzer 2 (Baixo)
bassNotes = (
  # 1. INTRO (compassos 1-8: o riff, as duas maos tocam)
  NOTE_B2, NOTE_REST, NOTE_B2, NOTE_REST, NOTE_B2, NOTE_A2,                             # compasso 1
  NOTE_REST, NOTE_B2, NOTE_REST, NOTE_D3, NOTE_REST, NOTE_B2,
  NOTE_REST, NOTE_FS2, NOTE_A2,
  NOTE_B2, NOTE_REST, NOTE_B2, NOTE_REST, NOTE_B2, NOTE_A2,                             # compasso 2
  NOTE_REST, NOTE_B2, NOTE_REST, NOTE_F3, NOTE_REST, NOTE_E3,
  NOTE_REST, NOTE_D3, NOTE_A2,
  NOTE_B2, NOTE_REST, NOTE_B2, NOTE_REST, NOTE_B2, NOTE_A2,                             # compasso 3
  NOTE_REST, NOTE_B2, NOTE_REST, NOTE_D3, NOTE_REST, NOTE_B2,
  NOTE_REST, NOTE_FS2, NOTE_A2,
  NOTE_B2, NOTE_REST, NOTE_B2, NOTE_REST, NOTE_B2, NOTE_A2,                             # compasso 4
  NOTE_REST, NOTE_B2, NOTE_REST, NOTE_F3, NOTE_REST, NOTE_E3,
  NOTE_REST, NOTE_B2, NOTE_A2,
  NOTE_B2, NOTE_REST, NOTE_B2, NOTE_REST, NOTE_B2, NOTE_A2,                             # compasso 5
  NOTE_REST, NOTE_B2, NOTE_REST, NOTE_D3, NOTE_REST, NOTE_B2,
  NOTE_REST, NOTE_FS2, NOTE_A2,
  NOTE_B2, NOTE_REST, NOTE_B2, NOTE_REST, NOTE_B2, NOTE_A2,                             # compasso 6
  NOTE_REST, NOTE_B2, NOTE_REST, NOTE_F3, NOTE_REST, NOTE_E3,
  NOTE_REST, NOTE_D3, NOTE_A2,
  NOTE_B2, NOTE_REST, NOTE_B2, NOTE_REST, NOTE_B2, NOTE_A2,                             # compasso 7
  NOTE_REST, NOTE_B2, NOTE_REST, NOTE_D3, NOTE_REST, NOTE_B2,
  NOTE_REST, NOTE_FS2, NOTE_A2,
  NOTE_B2, NOTE_REST, NOTE_B2, NOTE_REST, NOTE_B2, NOTE_REST,                           # compasso 8
  NOTE_A2, NOTE_B2, NOTE_REST,

  # 2. TEMA (compassos 9-24)
  NOTE_B2, NOTE_GS2, NOTE_REST, NOTE_REST, NOTE_REST,                                   # compasso 9
  NOTE_B2, NOTE_B2, NOTE_B2, NOTE_FS2, NOTE_FS2, NOTE_FS2,                              # compasso 10
  NOTE_B2, NOTE_GS2, NOTE_REST, NOTE_REST,                                              # compasso 11
  NOTE_CS3, NOTE_CS3, NOTE_CS3, NOTE_FS2, NOTE_FS2, NOTE_FS2,                           # compasso 12
  NOTE_B2, NOTE_GS2, NOTE_REST, NOTE_REST, NOTE_REST,                                   # compasso 13
  NOTE_B2, NOTE_B2, NOTE_B2, NOTE_FS2, NOTE_FS2, NOTE_FS2,                              # compasso 14
  NOTE_B2, NOTE_GS2, NOTE_GS2, NOTE_REST, NOTE_REST,                                    # compasso 15
  NOTE_CS3, NOTE_CS3, NOTE_CS3, NOTE_FS2, NOTE_FS2, NOTE_FS2,                           # compasso 16
  NOTE_B2, NOTE_GS2, NOTE_REST, NOTE_REST, NOTE_REST,                                   # compasso 17
  NOTE_B2, NOTE_B2, NOTE_B2, NOTE_FS2, NOTE_FS2, NOTE_FS2,                              # compasso 18
  NOTE_B2, NOTE_GS2, NOTE_REST, NOTE_REST,                                              # compasso 19
  NOTE_CS3, NOTE_CS3, NOTE_CS3, NOTE_FS2, NOTE_FS2, NOTE_FS2,                           # compasso 20
  NOTE_B2, NOTE_GS2, NOTE_REST, NOTE_REST, NOTE_REST,                                   # compasso 21
  NOTE_B2, NOTE_GS2, NOTE_REST, NOTE_REST,                                              # compasso 22
  NOTE_CS3, NOTE_CS3, NOTE_CS3, NOTE_FS2, NOTE_FS2, NOTE_FS2,                           # compasso 23
  NOTE_B2, NOTE_REST                                                                    # compasso 24
)

# Duracoes (ms)
noteDurations = (
  # 1. INTRO (compassos 1-8: o riff, as duas maos tocam)
  SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,   # compasso 1
  SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,
  SEMICOLCHEIA, SEMICOLCHEIA, COLCHEIA,
  SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,   # compasso 2
  SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,
  SEMICOLCHEIA, SEMICOLCHEIA, COLCHEIA,
  SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,   # compasso 3
  SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,
  SEMICOLCHEIA, SEMICOLCHEIA, COLCHEIA,
  SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,   # compasso 4
  SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,
  SEMICOLCHEIA, SEMICOLCHEIA, COLCHEIA,
  SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,   # compasso 5
  SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,
  SEMICOLCHEIA, SEMICOLCHEIA, COLCHEIA,
  SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,   # compasso 6
  SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,
  SEMICOLCHEIA, SEMICOLCHEIA, COLCHEIA,
  SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,   # compasso 7
  SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,
  SEMICOLCHEIA, SEMICOLCHEIA, COLCHEIA,
  SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,   # compasso 8
  SEMICOLCHEIA, SEMICOLCHEIA, MINIMA,

  # 2. TEMA (compassos 9-24)
  SEMINIMA_P, SEMINIMA_P, COLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,                         # compasso 9
  COLCHEIA_P, COLCHEIA_P, COLCHEIA, COLCHEIA_P, COLCHEIA_P, COLCHEIA,                   # compasso 10
  SEMINIMA_P, SEMINIMA_P, COLCHEIA, COLCHEIA,                                           # compasso 11
  COLCHEIA_P, COLCHEIA_P, COLCHEIA, COLCHEIA_P, COLCHEIA_P, COLCHEIA,                   # compasso 12
  SEMINIMA_P, SEMINIMA_P, COLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,                         # compasso 13
  COLCHEIA_P, COLCHEIA_P, COLCHEIA, COLCHEIA_P, COLCHEIA_P, COLCHEIA,                   # compasso 14
  SEMINIMA_P, SEMINIMA_P - GAP_MS, GAP_MS, COLCHEIA, COLCHEIA,                          # compasso 15
  COLCHEIA_P, COLCHEIA_P, COLCHEIA, COLCHEIA_P, COLCHEIA_P, COLCHEIA,                   # compasso 16
  SEMINIMA_P, SEMINIMA_P, COLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,                         # compasso 17
  COLCHEIA_P, COLCHEIA_P, COLCHEIA, COLCHEIA_P, COLCHEIA_P, COLCHEIA,                   # compasso 18
  SEMINIMA_P, SEMINIMA_P, COLCHEIA, COLCHEIA,                                           # compasso 19
  COLCHEIA_P, COLCHEIA_P, COLCHEIA, COLCHEIA_P, COLCHEIA_P, COLCHEIA,                   # compasso 20
  SEMINIMA_P, SEMINIMA_P, COLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,                         # compasso 21
  SEMINIMA_P, SEMINIMA_P, COLCHEIA, COLCHEIA,                                           # compasso 22
  COLCHEIA_P, COLCHEIA_P, COLCHEIA, COLCHEIA_P, COLCHEIA_P, COLCHEIA,                   # compasso 23
  SEMINIMA, MINIMA_P                                                                    # compasso 24
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
