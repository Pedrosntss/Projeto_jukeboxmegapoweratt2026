import serial
import time

PORTA = 'COM3'  # Linux: "/dev/ttyACM0" | Mac: "/dev/cu.usbmodemXXXX"

# ======================================================================
# JoJo's Bizarre Adventure: Golden Wind - Giorno's Theme (Ver. 2)
# Buzzer 1 = mão direita (nos acordes, a nota de cima)
# Buzzer 2 = mão esquerda (nos acordes, a nota de baixo)
# ======================================================================


# Frequências das notas, em Hz
NOTE_REST = 0
R = NOTE_REST

# Graves (mão esquerda)
NOTE_FS2 = 93    # Fá sustenido 2
NOTE_GS2 = 104   # Sol sustenido 2
NOTE_B2  = 123
NOTE_CS3 = 139   # Dó sustenido 3

# Introdução (as duas mãos tocam o riff aqui no grave)
NOTE_FS3 = 185
NOTE_A3  = 220
NOTE_B3  = 247
NOTE_D4  = 294
NOTE_E4  = 330
NOTE_F4  = 349

# Melodia do tema
NOTE_B4  = 494
NOTE_CS5 = 554
NOTE_D5  = 587
NOTE_E5  = 659
NOTE_F5  = 698
NOTE_FS5 = 740
NOTE_G5  = 784
NOTE_A5  = 880
NOTE_AS5 = 932   # Lá sustenido 5
NOTE_B5  = 988
NOTE_CS6 = 1109
NOTE_D6  = 1175
NOTE_E6  = 1319

# ---------- Oitava ----------
#   1 = original | 2 = sobe 1 oitava | 4 = sobe 2 oitavas
MULT_MELODIA = 1
MULT_BAIXO   = 2   # o baixo do tema é grave (Fá#2 = 93 Hz); se ficar fraco, ponha 4
# Na introdução (c. 1-8) as duas mãos tocam o mesmo riff, uma oitava
# separadas, bem no grave (Si3 e Si2). Ali as duas vozes usam o MULT_BAIXO,
# para o riff soar mais forte sem perder a oitava entre elas.

# ---------- Andamento (4/4, semínima = 130) ----------
# Para deixar a música mais rápida/lenta, mexa só no BPM.
BPM = 130
BEAT_MS = 60000 / BPM        # 1 tempo (semínima) em ms

# ---------- Articulação ----------
GAP_MS   = 30     # silêncio curto entre duas notas iguais seguidas (senão elas "grudam")
STACCATO = 0.5    # notas com ponto (staccato) soam só essa fração da duração


# ======================================================================
# Ferramentas para escrever a partitura
# Cada nota é (nota, tempos): semínima = 1, colcheia = 0.5, semicolcheia = 0.25.
# Notas ligadas (com arco de ligadura) já estão somadas numa nota só.
# ======================================================================
def S(nota, tempos):
    """Nota com ponto de staccato (curtinha)."""
    return (nota, tempos, True)

def oitava(voz, fator):
    """Multiplica as frequências de uma voz (fator 2 sobe 1 oitava, 0.5 desce)."""
    return [(n * fator,) + tuple(resto) for n, *resto in voz]

def articular(voz):
    """Converte tempos em ms; staccato soa só uma parte da nota e duas notas
    iguais seguidas ganham um respiro entre elas."""
    saida = []
    for i, nota in enumerate(voz):
        freq, tempos = nota[0], nota[1]
        stacc = len(nota) > 2 and nota[2]
        ms = tempos * BEAT_MS
        prox = voz[i + 1][0] if i + 1 < len(voz) else None
        if freq and stacc:
            saida += [(freq, ms * STACCATO), (R, ms * (1 - STACCATO))]
        elif freq and prox == freq:
            saida += [(freq, ms - GAP_MS), (R, GAP_MS)]
        else:
            saida.append((freq, ms))
    return saida

def juntar(melodia, baixo):
    """Junta as duas vozes em (melodia, baixo, duracao_ms), quebrando as notas
    longas onde a outra voz muda de nota."""
    eventos = []
    i = j = 0
    resto_m = melodia[0][1]
    resto_b = baixo[0][1]
    while i < len(melodia) and j < len(baixo):
        d = min(resto_m, resto_b)
        eventos.append((melodia[i][0], baixo[j][0], d))
        resto_m -= d
        resto_b -= d
        if resto_m < 0.01:
            i += 1
            resto_m = melodia[i][1] if i < len(melodia) else 0
        if resto_b < 0.01:
            j += 1
            resto_b = baixo[j][1] if j < len(baixo) else 0
    return eventos


# ======================================================================
# INTRODUÇÃO - compassos 1 a 8 (o riff)
# ======================================================================
# Tempos 1 e 2 são iguais em todos os compassos do riff
inicio = [S(NOTE_B3, 0.5), S(NOTE_B3, 0.5),
          (NOTE_B3, 0.25), (NOTE_A3, 0.25), (R, 0.25), (NOTE_B3, 0.25)]

riff_1 = inicio + [(R, 0.25), (NOTE_D4, 0.25), (R, 0.25), (NOTE_B3, 0.25),
                   (R, 0.25), (NOTE_FS3, 0.25), (NOTE_A3, 0.5)]        # c. 1, 3, 5, 7
riff_2 = inicio + [(R, 0.25), (NOTE_F4, 0.25), (R, 0.25), (NOTE_E4, 0.25),
                   (R, 0.25), (NOTE_D4, 0.25), (NOTE_A3, 0.5)]         # c. 2, 6
riff_4 = inicio + [(R, 0.25), (NOTE_F4, 0.25), (R, 0.25), (NOTE_E4, 0.25),
                   (R, 0.25), (NOTE_B3, 0.25), (NOTE_A3, 0.5)]         # c. 4
c8 = [S(NOTE_B3, 0.5), S(NOTE_B3, 0.5), S(NOTE_B3, 0.5),
      (NOTE_A3, 0.25), (NOTE_B3, 0.25), (R, 2)]

intro_md = riff_1 + riff_2 + riff_1 + riff_4 + riff_1 + riff_2 + riff_1 + c8
intro_me = oitava(intro_md, 0.5)     # a mão esquerda toca o mesmo riff, 1 oitava abaixo


# ======================================================================
# TEMA - compassos 9 a 24
# ======================================================================
# ---- Mão direita (frases que se repetem) ----
t_a = [(NOTE_FS5, 1.5), (NOTE_F5, 1.5), (R, 0.5), (NOTE_D5, 0.25), (NOTE_E5, 0.25)]   # c. 9, 13, 17, 21
t_b = [(NOTE_F5, 0.75), (NOTE_E5, 0.75), (NOTE_D5, 0.5),
       (NOTE_CS5, 0.75), (NOTE_D5, 0.75), (NOTE_E5, 0.5)]                               # c. 10, 14, 18
t_c = [(NOTE_FS5, 1.5), (NOTE_B5, 1.5), (NOTE_B4, 0.5), (NOTE_CS5, 0.5)]               # c. 11, 19, 22
t_d = [(NOTE_D5, 0.75), (NOTE_E5, 0.75), (NOTE_D5, 0.5),
       (NOTE_CS5, 0.75), (NOTE_A5, 0.75), (NOTE_G5, 0.5)]                               # c. 12, 20
c15 = [(NOTE_FS5, 1.5), (NOTE_B5, 1.5), (NOTE_B5, 0.5), (NOTE_CS6, 0.5)]
c16 = [(NOTE_D6, 0.75), (NOTE_E6, 0.75), (NOTE_G5, 0.5),                               # com 8va
       (NOTE_FS5, 0.75), (NOTE_D6, 0.75), (NOTE_E6, 0.5)]
c23 = [(NOTE_D5, 0.75), (NOTE_G5, 0.75), (NOTE_FS5, 0.5),
       (NOTE_F5, 0.75), (NOTE_D6, 0.75), (NOTE_AS5, 0.5)]
c24 = [(NOTE_B5, 1), (R, 3)]

tema_md = (t_a + t_b + t_c + t_d +        # 9-12
           t_a + t_b + c15 + c16 +        # 13-16
           t_a + t_b + t_c + t_d +        # 17-20
           t_a + t_c + c23 + c24)         # 21-24

# ---- Mão esquerda ----
b_x = [(NOTE_B2, 1.5), (NOTE_GS2, 1.5), (R, 1)]   # acorde de Si menor e depois Sol#
b_y = [(NOTE_B2, 2), (NOTE_FS2, 2)]               # c. 10, 14, 18
b_z = [(NOTE_CS3, 2), (NOTE_FS2, 2)]              # c. 12, 16, 20, 23
b24 = [(NOTE_B2, 1), (R, 3)]

tema_me = (b_x + b_y + b_x + b_z +        # 9-12
           b_x + b_y + b_x + b_z +        # 13-16
           b_x + b_y + b_x + b_z +        # 17-20
           b_x + b_x + b_z + b24)         # 21-24


# ======================================================================
# Monta a lista final (melodia, baixo, duração em ms)
# ======================================================================
melodia = articular(oitava(intro_md, MULT_BAIXO) + oitava(tema_md, MULT_MELODIA))
baixo   = articular(oitava(intro_me, MULT_BAIXO) + oitava(tema_me, MULT_BAIXO))
partitura = juntar(melodia, baixo)

melodyNotes   = tuple(n[0] for n in partitura)
bassNotes     = tuple(n[1] for n in partitura)
noteDurations = tuple(n[2] for n in partitura)


print("Conectando ao Arduino...")
arduino = serial.Serial(PORTA, 9600, timeout=5)
time.sleep(2)
print("Conectado! Tocando música...")

# Partitura: [Frequência Melodia, Frequência Baixo, Duração Total em ms]
for i in range(len(melodyNotes)):
    freq_m = int(melodyNotes[i])
    freq_b = int(bassNotes[i])
    duracao = int(noteDurations[i])

    # Envia o pacote completo para o Arduino (separado por espaços)
    comando = f"{freq_m} {freq_b} {duracao}\n"
    arduino.write(comando.encode('utf-8'))

    # Aguarda o Arduino terminar o acorde e responder "OK"
    resposta = arduino.readline()
    if not resposta:
        print("Arduino não respondeu na nota", i)

arduino.close()
print("Fim da música!")
