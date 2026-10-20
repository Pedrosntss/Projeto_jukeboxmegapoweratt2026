import serial
import time

PORTA = 'COM3'  # Linux: "/dev/ttyACM0" | Mac: "/dev/cu.usbmodemXXXX"

# ======================================================================
# Sua partitura - compassos 36 a 55 (páginas 3 e 4)
# Buzzer 1 = mão direita (nos acordes, a nota de cima)
# Buzzer 2 = mão esquerda (nos acordes, a nota de baixo)
# Armadura com 2 bemóis: todo Si e todo Mi são bemóis, a não ser que
# tenha um bequadro na partitura.
# ======================================================================


# Frequências das notas, em Hz
# (nomes no padrão do Arduino: "S" = sustenido. Mi bemol = Ré sustenido = NOTE_DS)
NOTE_REST = 0
R = NOTE_REST

# Graves (mão esquerda)
NOTE_G1  = 49
NOTE_D2  = 73
NOTE_DS2 = 78    # Mi bemol 2
NOTE_F2  = 87
NOTE_G2  = 98
NOTE_GS2 = 104   # Lá bemol 2
NOTE_A2  = 110
NOTE_C3  = 131
NOTE_D3  = 147
NOTE_DS3 = 156   # Mi bemol 3
NOTE_F3  = 175
NOTE_G3  = 196
NOTE_GS3 = 208   # Lá bemol 3
NOTE_A3  = 220

# Melodia (mão direita)
NOTE_D4  = 294
NOTE_G4  = 392
NOTE_GS4 = 415   # Lá bemol 4
NOTE_B4  = 494   # Si natural (bequadro)
NOTE_C5  = 523
NOTE_D5  = 587
NOTE_DS5 = 622   # Mi bemol 5
NOTE_E5  = 659   # Mi natural (bequadro)
NOTE_F5  = 698
NOTE_FS5 = 740   # Sol bemol 5
NOTE_G5  = 784
NOTE_GS5 = 831   # Lá bemol 5
NOTE_A5  = 880
NOTE_AS5 = 932   # Si bemol 5
NOTE_B5  = 988   # Si natural (bequadro)
NOTE_C6  = 1047
NOTE_D6  = 1175
NOTE_DS6 = 1245  # Mi bemol 6
NOTE_F6  = 1397
NOTE_FS6 = 1480  # Sol bemol 6
NOTE_G6  = 1568
NOTE_A6  = 1760
NOTE_D7  = 2349

# ---------- Oitava ----------
#   1 = original | 2 = sobe 1 oitava | 4 = sobe 2 oitavas
MULT_MELODIA = 1
MULT_BAIXO   = 2   # o baixo é bem grave (desce até Sol1 = 49 Hz); se ficar fraco, ponha 4

# ---------- Andamento (4/4) ----------
# As páginas 3 e 4 não mostram o andamento. Coloque aqui o BPM do começo da sua partitura.
BPM = 120
BEAT_MS = 60000 / BPM        # 1 tempo (semínima) em ms

# ---------- Articulação ----------
GAP_MS   = 30      # silêncio curto entre duas notas iguais seguidas (senão elas "grudam")
STACCATO = 0.5     # notas com ponto de staccato soam só essa fração da duração
TRINADO  = 1 / 8   # duração de cada nota do trinado, em tempos (1/8 = fusa)


# ======================================================================
# Ferramentas para escrever a partitura
# Cada nota é (nota, tempos): semínima = 1, colcheia = 0.5, semicolcheia = 0.25,
# e semicolcheia de tercina = 1/6. Ligaduras dentro do compasso já estão somadas.
# ======================================================================
T6 = 1 / 6

def S(nota, tempos):
    """Nota com ponto de staccato (curtinha)."""
    return (nota, tempos, 'st')

def L(nota, tempos):
    """Nota ligada à primeira nota do compasso seguinte (soa como uma nota só)."""
    return (nota, tempos, 'liga')

def trinado(nota, auxiliar, tempos):
    """Trinado: alterna a nota com a de cima, bem rápido."""
    n = round(tempos / TRINADO)
    return [(nota if i % 2 == 0 else auxiliar, TRINADO) for i in range(n)]

def oitava(voz, fator):
    """Multiplica as frequências de uma voz (fator 2 sobe 1 oitava)."""
    return [(n * fator,) + tuple(resto) for n, *resto in voz]

def articular(voz):
    """Converte tempos em ms: junta as ligaduras entre compassos, encurta os
    staccatos e põe um respiro entre duas notas iguais seguidas."""
    # 1) ligaduras que atravessam a barra de compasso
    unida = []
    for nota in voz:
        if unida and len(unida[-1]) > 2 and unida[-1][2] == 'liga' and unida[-1][0] == nota[0]:
            anterior = unida.pop()
            nota = (nota[0], anterior[1] + nota[1]) + tuple(nota[2:])
        unida.append(nota)
    # 2) staccato e respiro
    saida = []
    for i, nota in enumerate(unida):
        freq, tempos = nota[0], nota[1]
        marca = nota[2] if len(nota) > 2 else None
        ms = tempos * BEAT_MS
        prox = unida[i + 1][0] if i + 1 < len(unida) else None
        if freq and marca == 'st':
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
# MÃO DIREITA (melodia), compasso a compasso
# O ritmo base é 3+3+2: colcheia pontuada, colcheia pontuada, colcheia.
# ======================================================================
m = {}
m[36] = [(NOTE_D5, .75), (NOTE_DS5, .75), (NOTE_F5, .5), (NOTE_G5, .75), (NOTE_GS5, .75), (NOTE_AS5, .5)]
m[37] = [(NOTE_G5, .75), (NOTE_D5, .75), (NOTE_G5, .5), (NOTE_F5, .75), (NOTE_E5, .25), (NOTE_DS5, 1)]
m[38] = trinado(NOTE_D5, NOTE_DS5, 3.5) + [(NOTE_DS5, T6), (NOTE_D5, T6), (NOTE_C5, T6)]
m[39] = trinado(NOTE_B4, NOTE_C5, 3) + [(R, T6), (NOTE_D4, T6), (NOTE_G4, T6),
                                        (NOTE_GS4, T6), (NOTE_B4, T6), (NOTE_C5, T6)]
m[40] = m[36]
m[41] = [(NOTE_B5, .75), (NOTE_D6, .75), (NOTE_G6, .5), (NOTE_F6, 1), (NOTE_DS6, 1)]
m[42] = [S(NOTE_D6, .75), S(NOTE_D6, .75), S(NOTE_D6, .5),
         S(NOTE_DS6, .75), S(NOTE_DS6, .75), S(NOTE_DS6, .5)]
m[43] = [S(NOTE_D6, 1), (R, .5), (NOTE_AS5, 2.5)]
m[44] = [(NOTE_C5, .75), (NOTE_DS5, .75), (NOTE_G5, .5), (NOTE_FS5, 1), (NOTE_D5, .5), (NOTE_DS5, .5)]
m[45] = [(NOTE_F5, .75), (NOTE_DS5, .75), (NOTE_D5, 1), (NOTE_DS5, .5), (NOTE_G5, .5), (NOTE_B5, .5)]
m[46] = [(NOTE_D6, .75), (NOTE_C6, .75), (NOTE_DS6, 1), (NOTE_C6, .5), (NOTE_C6, .5), (NOTE_D6, .5)]
m[47] = [(NOTE_DS6, .75), (NOTE_B5, .75), (NOTE_C6, 1), (NOTE_G5, 1.5)]
m[48] = m[44]
m[49] = m[45]
m[50] = [(NOTE_D6, .75), (NOTE_C6, .75), (NOTE_DS6, 1), (NOTE_C6, .5), (NOTE_G6, .5), (NOTE_DS6, .5)]
m[51] = [(NOTE_D6, .75), (NOTE_D6, .75), (NOTE_C6, 1), (NOTE_C6, .5), (NOTE_DS6, .5), (NOTE_F6, .5)]
m[52] = [(NOTE_FS6, .75), (NOTE_F6, .5), (NOTE_DS6, .25), (NOTE_C6, .5),
         (R, .5), (NOTE_C5, .5), (NOTE_DS5, .5), (NOTE_F5, .5)]
m[53] = [(NOTE_FS5, .75), (NOTE_F5, .75), (NOTE_C5, .5), (R, .5), L(NOTE_D6, 1.5)]
m[54] = [(NOTE_D6, 3), (NOTE_D7, .25), (NOTE_A6, .25), (NOTE_G6, .25), (NOTE_DS6, .25)]  # 8va no fim
m[55] = [(NOTE_D7, 2), (NOTE_G6, 2)]                                                     # 8va

# ======================================================================
# MÃO ESQUERDA (baixo), compasso a compasso
# ======================================================================
b = {}
b[36] = [(NOTE_G2, .75), (NOTE_D3, .75), (NOTE_G3, .5), (NOTE_F3, .75), (NOTE_C3, .75), (NOTE_GS2, .5)]
b[37] = [(NOTE_G2, .75), (NOTE_D3, .75), (NOTE_G3, .5), (NOTE_GS3, .75), (NOTE_DS3, .75), (NOTE_GS2, .5)]
b[38] = [(NOTE_G2, .75), (NOTE_D3, .75), (NOTE_G3, .5), (NOTE_F2, .75), (NOTE_C3, .75), (NOTE_F3, .5)]
b[39] = [(NOTE_G2, .75), (NOTE_D3, .75), (NOTE_G2, .5), (NOTE_F3, .75), (NOTE_C3, .75), (NOTE_GS2, .5)]
b[40] = b[36]
b[41] = b[37]
b[42] = [S(NOTE_G2, .75), S(NOTE_G2, .75), S(NOTE_G2, .5),
         S(NOTE_GS2, .75), S(NOTE_F2, .75), S(NOTE_GS2, .5)]
b[43] = [S(NOTE_G2, 1), (R, .5), (NOTE_G2, 2.5)]     # oitava Sol1+Sol2: o buzzer toca o Sol2
b[44] = [(NOTE_C3, .75), (NOTE_DS3, .75), (NOTE_G3, .5),
         (NOTE_A2, .5), (NOTE_A2, .5), (NOTE_A3, .5), (NOTE_A2, .5)]
b[45] = [(NOTE_GS2, .75), (NOTE_G2, .75), (NOTE_C3, 1), (NOTE_G2, .5), (NOTE_C3, .5), (NOTE_G2, .5)]
b[46] = [(NOTE_A2, .75), (NOTE_A2, .75), (NOTE_GS2, 1), (NOTE_DS2, .5), (NOTE_GS2, .5), (NOTE_DS2, .5)]
b[47] = [(NOTE_G2, .75), (NOTE_G2, .75), (NOTE_C3, 1), (NOTE_G1, .5), (NOTE_D2, .5), (NOTE_G2, .5)]
b[48] = b[44]
b[49] = b[45]
b[50] = b[46]
b[51] = [(NOTE_G2, .75), (NOTE_G2, .75), (NOTE_C3, 1), (NOTE_C3, .5), (NOTE_DS3, .5), (NOTE_C3, .5)]
b[52] = b[51]
b[53] = [(NOTE_G2, .75), (NOTE_G2, .75), (NOTE_C3, 1), L(NOTE_C3, 1.5)]
b[54] = [(NOTE_C3, 4)]
b[55] = [(R, 4)]

COMPASSOS = range(36, 56)


# ======================================================================
# Monta a lista final (melodia, baixo, duração em ms)
# ======================================================================
mao_direita  = [nota for c in COMPASSOS for nota in m[c]]
mao_esquerda = [nota for c in COMPASSOS for nota in b[c]]

melodia = articular(oitava(mao_direita, MULT_MELODIA))
baixo   = articular(oitava(mao_esquerda, MULT_BAIXO))
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
