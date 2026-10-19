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
NOTE_D6 = 1175   # novas: a partitura chega ate o F6
NOTE_E6 = 1319
NOTE_F6 = 1397

# ---------- Oitava ----------
# Agora as notas da MELODIA estao escritas na mesma altura da partitura
# (por isso MULT_MELODIA = 1). O baixo continua subindo uma oitava,
# porque buzzer pequeno soa muito fraco abaixo de ~300 Hz.
#   1 = original | 2 = sobe 1 oitava | 4 = sobe 2 oitavas
# Se a 2a parte (grave) ficar fraca, ponha MULT_MELODIA = 2.
MULT_MELODIA = 1
MULT_BAIXO  = 2

# ---------- Andamento (compasso 3/4) ----------
# Partitura: seminima = 200 BPM -> 300 ms por tempo.
# Para deixar a musica mais rapida/lenta, mexa so no BEAT_MS.
BEAT_MS  = 300                # 1 tempo (seminima) em ms -> 200 BPM
COLCHEIA = (BEAT_MS / 2)      # 1/2 tempo
SEMINIMA = (BEAT_MS)          # 1 tempo
MINIMA   = (BEAT_MS * 2)      # 2 tempos
MINIMA_P = (BEAT_MS * 3)      # 3 tempos (compasso inteiro)

# Atalhos so para deixar a partitura abaixo mais legivel
R   = NOTE_REST
COL = COLCHEIA
SEM = SEMINIMA
MIN = MINIMA
MIN_P = MINIMA_P


# ======================================================================
# PARTITURA, compasso a compasso
# Cada compasso e uma lista de (melodia, baixo, duracao_ms)
#   melodia = voz de cima da mao direita
#   baixo   = nota grave da mao esquerda
# Os numeros dos compassos seguem a partitura (1 a 38).
# ======================================================================

# ---- Compassos de acompanhamento ("pa-pa") ----
def dm():   # D menor (compassos 1, 5, 22, ...)
    return [(R, NOTE_D3, SEM), (NOTE_A4, NOTE_D3, SEM), (NOTE_A4, NOTE_D3, SEM)]

def em():   # E menor, com a nota E4 ligada ao acorde (compassos 2, 4, 6, 8, ...)
    return [(R, NOTE_E3, COL), (NOTE_E4, NOTE_E3, COL), (NOTE_B4, NOTE_E3, MIN)]

def fm():   # F maior (compassos 3, 7, 20, 24, ...)
    return [(R, NOTE_F3, SEM), (NOTE_C5, NOTE_F3, SEM), (NOTE_C5, NOTE_F3, SEM)]

# ---- Parte A (oitava de cima) - compassos 9 a 18 ----
c9  = [(NOTE_D5, NOTE_D3, COL), (NOTE_F5, NOTE_D3, COL), (NOTE_D6, NOTE_D3, MIN)]
c10 = [(NOTE_D5, NOTE_E3, COL), (NOTE_F5, NOTE_E3, COL), (NOTE_D6, NOTE_E3, MIN)]
c11 = [(NOTE_E6, NOTE_F3, SEM), (R, NOTE_F3, COL),
       (NOTE_F6, NOTE_F3, COL), (NOTE_E6, NOTE_F3, COL), (NOTE_F6, NOTE_F3, COL)]
c12 = [(NOTE_E6, NOTE_E3, COL), (NOTE_C6, NOTE_E3, COL), (NOTE_A5, NOTE_E3, MIN)]
c13 = [(NOTE_A5, R, SEM), (NOTE_D5, NOTE_D3, SEM),
       (NOTE_F5, NOTE_D3, COL), (NOTE_G5, NOTE_D3, COL)]
c14 = [(NOTE_A5, NOTE_G3, MIN_P)]
c15 = c13
c16 = [(NOTE_E5, NOTE_A3, MIN_P)]
c17 = [(NOTE_A5, NOTE_A3, MIN), (NOTE_A5, NOTE_A3, SEM)]   # 2a vez (volta 2)
c18 = [(NOTE_D5, NOTE_D3, MIN_P)]

# ---- Parte B (oitava de baixo) - compassos 26 a 35 ----
c26 = [(NOTE_D4, NOTE_D3, COL), (NOTE_F4, NOTE_D3, COL), (NOTE_D5, NOTE_D3, MIN)]
c27 = [(NOTE_D4, NOTE_E3, COL), (NOTE_F4, NOTE_E3, COL), (NOTE_D5, NOTE_E3, MIN)]
c28 = [(NOTE_E5, NOTE_F3, SEM), (R, NOTE_F3, COL),
       (NOTE_F5, NOTE_F3, COL), (NOTE_E5, NOTE_F3, COL), (NOTE_F5, NOTE_F3, COL)]
c29 = [(NOTE_E5, NOTE_E3, COL), (NOTE_C5, NOTE_E3, COL), (NOTE_A4, NOTE_E3, MIN)]
c30 = [(NOTE_A4, R, SEM), (NOTE_D4, NOTE_D3, SEM),
       (NOTE_F4, NOTE_D3, COL), (NOTE_G4, NOTE_D3, COL)]
c31 = [(NOTE_A4, NOTE_G3, MIN_P)]
c32 = c30
c33 = [(NOTE_E4, NOTE_A3, MIN_P)]
c34 = [(NOTE_A4, NOTE_A3, MIN), (NOTE_A4, NOTE_A3, SEM)]   # 2a vez (volta 2)
c35 = [(NOTE_D4, NOTE_D3, MIN_P)]

# ---- Ordem de execucao (repeticoes, voltas e D.S. al Fine) ----
# Compassos 1-8: introducao (D menor, E menor, F, E menor, duas vezes)
intro = dm() + em() + fm() + em() + dm() + em() + fm() + em()

# Compassos 9-16 (1a vez, passa por todas as casas) -> repete
parte_a_1 = c9 + c10 + c11 + c12 + c13 + c14 + c15 + c16

# 2a vez: 9-13, pula 14-16, vai para a casa 2 (compasso 17)
# e segue pelos compassos 18-25 (acompanhamento)
parte_a_2 = (c9 + c10 + c11 + c12 + c13 + c17 +
             c18 + em() + fm() + em() + dm() + em() + fm() + em())

# Compassos 26-33 (1a vez) -> repete
parte_b_1 = c26 + c27 + c28 + c29 + c30 + c31 + c32 + c33

# 2a vez: 26-30, pula para o compasso 34 e fecha com os compassos 35-38
parte_b_2 = (c26 + c27 + c28 + c29 + c30 + c34 +
             c35 + em() + fm() + em())

# D.S. al Fine: volta ao segno (compasso 5) e toca ate o Fine (compasso 8)
final = dm() + em() + fm() + em()

partitura = intro + parte_a_1 + parte_a_2 + parte_b_1 + parte_b_2 + final

melodyNotes   = tuple(n[0] for n in partitura)
bassNotes     = tuple(n[1] for n in partitura)
noteDurations = tuple(n[2] for n in partitura)


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
