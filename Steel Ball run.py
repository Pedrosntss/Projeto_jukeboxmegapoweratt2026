import serial
import time

PORTA = 'COM3'  # Linux: "/dev/ttyACM0" | Mac: "/dev/cu.usbmodemXXXX"

# ======================================================================
# Sua partitura - compassos 36 a 55 (páginas 3 e 4)
# Buzzer 1 = mão direita (nos acordes, a nota de cima)
# Buzzer 2 = mão esquerda (nos acordes, a nota de baixo)
# Armadura com 2 bemóis: todo Si e todo Mi são bemóis, a não ser que
# tenha um bequadro na partitura. Nomes no padrão do Arduino:
# "S" = sustenido (Mi bemol = Ré sustenido = NOTE_DS).
# ======================================================================


# Frequências das notas, em Hz
NOTE_REST = 0

# Notas do Baixo (Graves)
NOTE_G1 = 49
NOTE_D2 = 73
NOTE_DS2= 78    # Mi bemol 2
NOTE_F2 = 87
NOTE_G2 = 98
NOTE_GS2= 104   # Lá bemol 2
NOTE_A2 = 110
NOTE_C3 = 131
NOTE_D3 = 147
NOTE_DS3= 156   # Mi bemol 3
NOTE_E3 = 165
NOTE_F3 = 175
NOTE_FS3= 185
NOTE_G3 = 196
NOTE_GS3= 208   # Lá bemol 3
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
NOTE_GS4= 415   # Lá bemol 4
NOTE_A4 = 440
NOTE_AS4= 466
NOTE_B4 = 494   # Si natural (bequadro)
NOTE_C5 = 523
NOTE_CS5= 554
NOTE_D5 = 587
NOTE_DS5= 622   # Mi bemol 5
NOTE_E5 = 659   # Mi natural (bequadro)
NOTE_F5 = 698
NOTE_FS5= 740   # Sol bemol 5
NOTE_G5 = 784
NOTE_GS5= 831   # Lá bemol 5
NOTE_A5 = 880
NOTE_AS5= 932   # Si bemol 5
NOTE_B5 = 988   # Si natural (bequadro)
NOTE_C6 = 1047
NOTE_D6 = 1175
NOTE_DS6= 1245  # Mi bemol 6
NOTE_F6 = 1397
NOTE_FS6= 1480  # Sol bemol 6
NOTE_G6 = 1568
NOTE_A6 = 1760
NOTE_D7 = 2349

# ---------- Oitava ----------
# Multiplicador da frequencia:
#   1 = original | 2 = sobe 1 oitava | 4 = sobe 2 oitavas
# A melodia fica como na partitura e o baixo sobe uma oitava (ele desce ate
# Sol1 = 49 Hz, grave demais para o buzzer). Se o baixo ficar fraco, ponha 4.
# Com estes valores: melodia toca de 294 a 2349 Hz; baixo toca de 98 a 440 Hz.
MULT_MELODIA = 1
MULT_BAIXO  = 2

# ---------- Andamento (compasso 4/4) ----------
# As paginas 3 e 4 nao mostram o andamento. Coloque aqui o BPM do comeco da
# sua partitura. Para deixar a musica mais rapida/lenta, mexa so no BEAT_MS.
BEAT_MS  = 500                # 1 tempo (seminima) em ms -> 120 BPM
FUSA           = (BEAT_MS / 8)      # 1/8 tempo (nota do trinado)
SEMICOLCHEIA_T = (BEAT_MS / 6)      # 1/6 tempo (semicolcheia de tercina)
SEMICOLCHEIA   = (BEAT_MS / 4)      # 1/4 tempo
SEMICOLCHEIA_P = (BEAT_MS * 3 / 8)  # 3/8 tempo (semicolcheia pontuada)
COLCHEIA       = (BEAT_MS / 2)      # 1/2 tempo
COLCHEIA_P     = (BEAT_MS * 3 / 4)  # 3/4 tempo (colcheia pontuada)
SEMINIMA       = (BEAT_MS)          # 1 tempo
MINIMA         = (BEAT_MS * 2)      # 2 tempos
MINIMA_C       = (BEAT_MS * 2.5)    # 2,5 tempos (minima + colcheia)
SEMIBREVE_C    = (BEAT_MS * 4.5)    # 4,5 tempos (semibreve + colcheia, nota ligada)

# Silencio entre as notas: 25% da duracao, mas no maximo GAP_MAX_MS
# (evita "buracos" enormes no meio das notas longas)
GAP_RATIO = 0.25
GAP_MAX_MS = 60


# Partitura - Buzzer 1 (Melodia)
melodyNotes = (
  # 1. COMPASSOS 36 a 39
  NOTE_D5, NOTE_DS5, NOTE_F5, NOTE_G5, NOTE_GS5, NOTE_AS5,        # compasso 36
  NOTE_G5, NOTE_D5, NOTE_G5, NOTE_F5, NOTE_E5, NOTE_DS5,          # compasso 37
  NOTE_DS5,                                                       # compasso 37 (cont.)
  NOTE_D5, NOTE_DS5, NOTE_D5, NOTE_DS5, NOTE_D5, NOTE_DS5,        # compasso 38
  NOTE_D5, NOTE_DS5, NOTE_D5, NOTE_DS5, NOTE_D5, NOTE_DS5,        # compasso 38 (cont.)
  NOTE_D5, NOTE_DS5, NOTE_D5, NOTE_DS5, NOTE_D5, NOTE_DS5,        # compasso 38 (cont.)
  NOTE_D5, NOTE_DS5, NOTE_D5, NOTE_DS5, NOTE_D5, NOTE_DS5,        # compasso 38 (cont.)
  NOTE_D5, NOTE_DS5, NOTE_D5, NOTE_DS5, NOTE_DS5, NOTE_D5,        # compasso 38 (cont.)
  NOTE_C5,                                                        # compasso 38 (cont.)
  NOTE_B4, NOTE_C5, NOTE_B4, NOTE_C5, NOTE_B4, NOTE_C5,           # compasso 39
  NOTE_B4, NOTE_C5, NOTE_B4, NOTE_C5, NOTE_B4, NOTE_C5,           # compasso 39 (cont.)
  NOTE_B4, NOTE_C5, NOTE_B4, NOTE_C5, NOTE_B4, NOTE_C5,           # compasso 39 (cont.)
  NOTE_B4, NOTE_C5, NOTE_B4, NOTE_C5, NOTE_B4, NOTE_C5,           # compasso 39 (cont.)
  NOTE_REST, NOTE_D4, NOTE_G4, NOTE_GS4, NOTE_B4, NOTE_C5,        # compasso 39 (cont.)

  # 2. COMPASSOS 40 a 43
  NOTE_D5, NOTE_DS5, NOTE_F5, NOTE_G5, NOTE_GS5, NOTE_AS5,        # compasso 40
  NOTE_B5, NOTE_D6, NOTE_G6, NOTE_F6, NOTE_F6, NOTE_DS6,          # compasso 41
  NOTE_DS6,                                                       # compasso 41 (cont.)
  NOTE_D6, NOTE_REST, NOTE_D6, NOTE_REST, NOTE_D6, NOTE_REST,     # compasso 42
  NOTE_DS6, NOTE_REST, NOTE_DS6, NOTE_REST, NOTE_DS6, NOTE_REST,  # compasso 42 (cont.)
  NOTE_D6, NOTE_REST, NOTE_AS5,                                   # compasso 43

  # 3. COMPASSOS 44 a 47
  NOTE_C5, NOTE_DS5, NOTE_G5, NOTE_FS5, NOTE_FS5, NOTE_D5,        # compasso 44
  NOTE_DS5,                                                       # compasso 44 (cont.)
  NOTE_F5, NOTE_DS5, NOTE_D5, NOTE_DS5, NOTE_G5, NOTE_B5,         # compasso 45
  NOTE_D6, NOTE_C6, NOTE_DS6, NOTE_C6, NOTE_C6, NOTE_D6,          # compasso 46
  NOTE_DS6, NOTE_B5, NOTE_C6, NOTE_G5, NOTE_G5, NOTE_G5,          # compasso 47

  # 4. COMPASSOS 48 a 51
  NOTE_C5, NOTE_DS5, NOTE_G5, NOTE_FS5, NOTE_FS5, NOTE_D5,        # compasso 48
  NOTE_DS5,                                                       # compasso 48 (cont.)
  NOTE_F5, NOTE_DS5, NOTE_D5, NOTE_DS5, NOTE_G5, NOTE_B5,         # compasso 49
  NOTE_D6, NOTE_C6, NOTE_DS6, NOTE_C6, NOTE_G6, NOTE_DS6,         # compasso 50
  NOTE_D6, NOTE_D6, NOTE_C6, NOTE_C6, NOTE_DS6, NOTE_F6,          # compasso 51

  # 5. COMPASSOS 52 a 55 (final, ultima nota alongada)
  NOTE_FS6, NOTE_F6, NOTE_DS6, NOTE_C6, NOTE_REST, NOTE_C5,       # compasso 52
  NOTE_DS5, NOTE_F5,                                              # compasso 52 (cont.)
  NOTE_FS5, NOTE_F5, NOTE_C5, NOTE_REST, NOTE_D6,                 # compasso 53 (a ultima nota continua ate o compasso 54)
  NOTE_D7, NOTE_A6, NOTE_G6, NOTE_DS6,                            # compasso 54
  NOTE_D7, NOTE_G6                                                # compasso 55
)

# Partitura - Buzzer 2 (Baixo)
bassNotes = (
  # 1. COMPASSOS 36 a 39
  NOTE_G2, NOTE_D3, NOTE_G3, NOTE_F3, NOTE_C3, NOTE_GS2,         # compasso 36
  NOTE_G2, NOTE_D3, NOTE_G3, NOTE_GS3, NOTE_DS3, NOTE_DS3,       # compasso 37
  NOTE_GS2,                                                      # compasso 37 (cont.)
  NOTE_G2, NOTE_G2, NOTE_G2, NOTE_G2, NOTE_G2, NOTE_G2,          # compasso 38
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,          # compasso 38 (cont.)
  NOTE_G3, NOTE_G3, NOTE_G3, NOTE_G3, NOTE_F2, NOTE_F2,          # compasso 38 (cont.)
  NOTE_F2, NOTE_F2, NOTE_F2, NOTE_F2, NOTE_C3, NOTE_C3,          # compasso 38 (cont.)
  NOTE_C3, NOTE_C3, NOTE_C3, NOTE_C3, NOTE_F3, NOTE_F3,          # compasso 38 (cont.)
  NOTE_F3,                                                       # compasso 38 (cont.)
  NOTE_G2, NOTE_G2, NOTE_G2, NOTE_G2, NOTE_G2, NOTE_G2,          # compasso 39
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3, NOTE_D3,          # compasso 39 (cont.)
  NOTE_G2, NOTE_G2, NOTE_G2, NOTE_G2, NOTE_F3, NOTE_F3,          # compasso 39 (cont.)
  NOTE_F3, NOTE_F3, NOTE_F3, NOTE_F3, NOTE_C3, NOTE_C3,          # compasso 39 (cont.)
  NOTE_C3, NOTE_C3, NOTE_C3, NOTE_GS2, NOTE_GS2, NOTE_GS2,       # compasso 39 (cont.)

  # 2. COMPASSOS 40 a 43
  NOTE_G2, NOTE_D3, NOTE_G3, NOTE_F3, NOTE_C3, NOTE_GS2,         # compasso 40
  NOTE_G2, NOTE_D3, NOTE_G3, NOTE_GS3, NOTE_DS3, NOTE_DS3,       # compasso 41
  NOTE_GS2,                                                      # compasso 41 (cont.)
  NOTE_G2, NOTE_REST, NOTE_G2, NOTE_REST, NOTE_G2, NOTE_REST,    # compasso 42
  NOTE_GS2, NOTE_REST, NOTE_F2, NOTE_REST, NOTE_GS2, NOTE_REST,  # compasso 42 (cont.)
  NOTE_G2, NOTE_REST, NOTE_G2,                                   # compasso 43

  # 3. COMPASSOS 44 a 47
  NOTE_C3, NOTE_DS3, NOTE_G3, NOTE_A2, NOTE_A2, NOTE_A3,         # compasso 44
  NOTE_A2,                                                       # compasso 44 (cont.)
  NOTE_GS2, NOTE_G2, NOTE_C3, NOTE_G2, NOTE_C3, NOTE_G2,         # compasso 45
  NOTE_A2, NOTE_A2, NOTE_GS2, NOTE_DS2, NOTE_GS2, NOTE_DS2,      # compasso 46
  NOTE_G2, NOTE_G2, NOTE_C3, NOTE_G1, NOTE_D2, NOTE_G2,          # compasso 47

  # 4. COMPASSOS 48 a 51
  NOTE_C3, NOTE_DS3, NOTE_G3, NOTE_A2, NOTE_A2, NOTE_A3,         # compasso 48
  NOTE_A2,                                                       # compasso 48 (cont.)
  NOTE_GS2, NOTE_G2, NOTE_C3, NOTE_G2, NOTE_C3, NOTE_G2,         # compasso 49
  NOTE_A2, NOTE_A2, NOTE_GS2, NOTE_DS2, NOTE_GS2, NOTE_DS2,      # compasso 50
  NOTE_G2, NOTE_G2, NOTE_C3, NOTE_C3, NOTE_DS3, NOTE_C3,         # compasso 51

  # 5. COMPASSOS 52 a 55 (final, ultima nota alongada)
  NOTE_G2, NOTE_G2, NOTE_G2, NOTE_C3, NOTE_C3, NOTE_C3,          # compasso 52
  NOTE_DS3, NOTE_C3,                                             # compasso 52 (cont.)
  NOTE_G2, NOTE_G2, NOTE_C3, NOTE_C3, NOTE_C3,                   # compasso 53 (a ultima nota continua ate o compasso 54)
  NOTE_C3, NOTE_C3, NOTE_C3, NOTE_C3,                            # compasso 54
  NOTE_REST, NOTE_REST                                           # compasso 55
)

# Duracoes (ms)
noteDurations = (
  # 1. COMPASSOS 36 a 39
  COLCHEIA_P, COLCHEIA_P, COLCHEIA, COLCHEIA_P, COLCHEIA_P, COLCHEIA,                              # compasso 36
  COLCHEIA_P, COLCHEIA_P, COLCHEIA, COLCHEIA_P, SEMICOLCHEIA, COLCHEIA,                            # compasso 37
  COLCHEIA,                                                                                        # compasso 37 (cont.)
  FUSA, FUSA, FUSA, FUSA, FUSA, FUSA,                                                              # compasso 38
  FUSA, FUSA, FUSA, FUSA, FUSA, FUSA,                                                              # compasso 38 (cont.)
  FUSA, FUSA, FUSA, FUSA, FUSA, FUSA,                                                              # compasso 38 (cont.)
  FUSA, FUSA, FUSA, FUSA, FUSA, FUSA,                                                              # compasso 38 (cont.)
  FUSA, FUSA, FUSA, FUSA, SEMICOLCHEIA_T, SEMICOLCHEIA_T,                                          # compasso 38 (cont.)
  SEMICOLCHEIA_T,                                                                                  # compasso 38 (cont.)
  FUSA, FUSA, FUSA, FUSA, FUSA, FUSA,                                                              # compasso 39
  FUSA, FUSA, FUSA, FUSA, FUSA, FUSA,                                                              # compasso 39 (cont.)
  FUSA, FUSA, FUSA, FUSA, FUSA, FUSA,                                                              # compasso 39 (cont.)
  FUSA, FUSA, FUSA, FUSA, FUSA, FUSA,                                                              # compasso 39 (cont.)
  SEMICOLCHEIA_T, SEMICOLCHEIA_T, SEMICOLCHEIA_T, SEMICOLCHEIA_T, SEMICOLCHEIA_T, SEMICOLCHEIA_T,  # compasso 39 (cont.)

  # 2. COMPASSOS 40 a 43
  COLCHEIA_P, COLCHEIA_P, COLCHEIA, COLCHEIA_P, COLCHEIA_P, COLCHEIA,                              # compasso 40
  COLCHEIA_P, COLCHEIA_P, COLCHEIA, COLCHEIA_P, SEMICOLCHEIA, COLCHEIA,                            # compasso 41
  COLCHEIA,                                                                                        # compasso 41 (cont.)
  SEMICOLCHEIA_P, SEMICOLCHEIA_P, SEMICOLCHEIA_P, SEMICOLCHEIA_P, SEMICOLCHEIA, SEMICOLCHEIA,      # compasso 42
  SEMICOLCHEIA_P, SEMICOLCHEIA_P, SEMICOLCHEIA_P, SEMICOLCHEIA_P, SEMICOLCHEIA, SEMICOLCHEIA,      # compasso 42 (cont.)
  COLCHEIA, SEMINIMA, MINIMA_C,                                                                    # compasso 43

  # 3. COMPASSOS 44 a 47
  COLCHEIA_P, COLCHEIA_P, COLCHEIA, COLCHEIA, COLCHEIA, COLCHEIA,                                  # compasso 44
  COLCHEIA,                                                                                        # compasso 44 (cont.)
  COLCHEIA_P, COLCHEIA_P, SEMINIMA, COLCHEIA, COLCHEIA, COLCHEIA,                                  # compasso 45
  COLCHEIA_P, COLCHEIA_P, SEMINIMA, COLCHEIA, COLCHEIA, COLCHEIA,                                  # compasso 46
  COLCHEIA_P, COLCHEIA_P, SEMINIMA, COLCHEIA, COLCHEIA, COLCHEIA,                                  # compasso 47

  # 4. COMPASSOS 48 a 51
  COLCHEIA_P, COLCHEIA_P, COLCHEIA, COLCHEIA, COLCHEIA, COLCHEIA,                                  # compasso 48
  COLCHEIA,                                                                                        # compasso 48 (cont.)
  COLCHEIA_P, COLCHEIA_P, SEMINIMA, COLCHEIA, COLCHEIA, COLCHEIA,                                  # compasso 49
  COLCHEIA_P, COLCHEIA_P, SEMINIMA, COLCHEIA, COLCHEIA, COLCHEIA,                                  # compasso 50
  COLCHEIA_P, COLCHEIA_P, SEMINIMA, COLCHEIA, COLCHEIA, COLCHEIA,                                  # compasso 51

  # 5. COMPASSOS 52 a 55 (final, ultima nota alongada)
  COLCHEIA_P, COLCHEIA, SEMICOLCHEIA, COLCHEIA, COLCHEIA, COLCHEIA,                                # compasso 52
  COLCHEIA, COLCHEIA,                                                                              # compasso 52 (cont.)
  COLCHEIA_P, COLCHEIA_P, COLCHEIA, COLCHEIA, SEMIBREVE_C,                                         # compasso 53 (a ultima nota continua ate o compasso 54)
  SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA, SEMICOLCHEIA,                                          # compasso 54
  MINIMA, MINIMA                                                                                   # compasso 55
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
