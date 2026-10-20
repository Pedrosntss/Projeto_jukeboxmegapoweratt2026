import serial
import time

PORTA = 'COM3'  # Linux: "/dev/ttyACM0" | Mac: "/dev/cu.usbmodemXXXX"

# ======================================================================
# Pirates of the Caribbean - He's a Pirate (versão para piano)
# Buzzer 1 = mão direita (melodia)
# Buzzer 2 = mão esquerda (baixo, uma nota por compasso)
# Ré menor, compasso 3/4, semínima = 150
#
# Estrutura da partitura (67 compassos):
#   c. 1        anacruse (compasso rosa)
#   c. 2-17     parte A, com ritornelo: casa 1 = c. 16-17, casa 2 = c. 18
#   c. 18-26    casa 2 e ponte
#   c. 27-34    parte B
#   c. 35-51    parte C
#   c. 52-67    FINAL (volta o tema)
# ======================================================================


# Frequências das notas, em Hz
NOTE_REST = 0
R = NOTE_REST

# Graves (mão esquerda)
NOTE_F2  = 87
NOTE_G2  = 98
NOTE_A2  = 110
NOTE_BB2 = 117   # Si bemol 2
NOTE_C3  = 131
NOTE_D3  = 147

# Melodia (mão direita)
NOTE_A3  = 220
NOTE_BB3 = 233   # Si bemol 3 (só no compasso 24)
NOTE_C4  = 262
NOTE_CS4 = 277   # Dó sustenido 4
NOTE_D4  = 294
NOTE_E4  = 330
NOTE_F4  = 349
NOTE_G4  = 392
NOTE_A4  = 440
NOTE_BB4 = 466   # Si bemol 4

# ---------- Oitava ----------
#   1 = original | 2 = sobe 1 oitava | 4 = sobe 2 oitavas
#   (use só 1, 2 ou 4: o 3 não é oitava e muda as notas do baixo)
#   Deixe os dois iguais: assim a distância entre melodia e baixo fica como na partitura
#   e os dois buzzers não caem na mesma frequência.
MULT_MELODIA = 4  # a melodia vai de Lá3 a Si bemol4 (220-466 Hz); com 4 toca de 880 a 1864 Hz
MULT_BAIXO   = 4  # o baixo desce até Fá2 (87 Hz), grave demais para um buzzer; com 4 toca de 349 a 587 Hz

# ---------- Andamento (3/4, semínima = 150) ----------
# A partitura não mostra o andamento. Para deixar a música mais rápida/lenta, mexa só no BPM.
BPM = 150
BEAT_MS = 60000 / BPM        # 1 tempo (semínima) em ms

# ---------- Repetição ----------
# O ritornelo (casa 1 / casa 2) já está na ordem dos compassos, mais abaixo (COMPASSOS).
REPETICOES = 1     # quantas vezes a música toca do começo ao fim; 0 = repete para sempre (Ctrl+C para parar)

# ---------- Articulação ----------
GAP_MS   = 30      # silêncio curto entre duas notas iguais seguidas (senão elas "grudam")
STACCATO = 0.5     # notas com ponto de staccato soam só essa fração da duração


# ======================================================================
# Ferramentas para escrever a partitura
# Cada nota é (nota, tempos): semínima = 1, colcheia = 0.5, semicolcheia = 0.25.
# ======================================================================
def S(nota, tempos):
    """Nota com ponto de staccato (curtinha). Não é usada nesta partitura."""
    return (nota, tempos, 'st')

def L(nota, tempos):
    """Nota ligada à nota seguinte, de mesma altura (soa como uma nota só)."""
    return (nota, tempos, 'liga')

def oitava(voz, fator):
    """Multiplica as frequências de uma voz (fator 2 sobe 1 oitava)."""
    return [(n * fator,) + tuple(resto) for n, *resto in voz]

def articular(voz):
    """Converte tempos em ms: junta as ligaduras, encurta os
    staccatos e põe um respiro entre duas notas iguais seguidas."""
    # 1) ligaduras (dentro do compasso ou atravessando a barra de compasso)
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
# Os comentários mostram as notas para você conferir com a partitura.
# ======================================================================
m = {}
# ---- Parte A (c. 1-17): anacruse + tema ----
m[1]  = [(NOTE_A3, .5), (NOTE_C4, .5)]                                      # anacruse: Lá Dó
m[2]  = [(NOTE_D4, 1), (NOTE_D4, 1), (NOTE_D4, .5), (NOTE_E4, .5)]          # Ré Ré Ré Mi
m[3]  = [(NOTE_F4, 1), (NOTE_F4, 1), (NOTE_F4, .5), (NOTE_G4, .5)]          # Fá Fá Fá Sol
m[4]  = [(NOTE_E4, 1), (NOTE_E4, 1), (NOTE_D4, .5), (NOTE_C4, .5)]          # Mi Mi Ré Dó
m[5]  = [(NOTE_C4, .5), L(NOTE_D4, .5), (NOTE_D4, 1), (NOTE_A3, .5), (NOTE_C4, .5)]   # Dó Ré~Ré, Lá Dó
m[6]  = m[2]
m[7]  = m[3]
m[8]  = m[4]
m[9]  = [(NOTE_D4, 1), (R, 1), (NOTE_A3, .5), (NOTE_C4, .5)]                # Ré (pausa) Lá Dó
m[10] = [(NOTE_D4, 1), (NOTE_D4, 1), (NOTE_D4, .5), (NOTE_F4, .5)]          # Ré Ré Ré Fá
m[11] = [(NOTE_G4, 1), (NOTE_G4, 1), (NOTE_G4, .5), (NOTE_A4, .5)]          # Sol Sol Sol Lá
m[12] = [(NOTE_BB4, 1), (NOTE_BB4, 1), (NOTE_A4, .5), (NOTE_G4, .5)]        # Si♭ Si♭ Lá Sol
m[13] = [(NOTE_A4, .5), L(NOTE_D4, .5), (NOTE_D4, 1), (NOTE_D4, .5), (NOTE_E4, .5)]   # Lá Ré~Ré Ré Mi
m[14] = [(NOTE_F4, 1), (NOTE_F4, 1), (NOTE_G4, 1)]                          # Fá Fá Sol
m[15] = [(NOTE_A4, .5), L(NOTE_D4, .5), (NOTE_D4, 1), (NOTE_D4, .5), (NOTE_F4, .5)]   # Lá Ré~Ré Ré Fá
m[16] = [(NOTE_E4, 1), (NOTE_E4, 1), (NOTE_F4, .5), (NOTE_D4, .5)]          # casa 1: Mi Mi Fá Ré
m[17] = [(NOTE_E4, 1), (R, 1), (NOTE_A3, .5), (NOTE_C4, .5)]                # casa 1: Mi (pausa) Lá Dó -> volta ao c. 2

# ---- Casa 2 e ponte (c. 18-26) ----
m[18] = [(NOTE_E4, 1), (NOTE_E4, 1), (NOTE_D4, .5), (NOTE_CS4, .5)]         # casa 2: Mi Mi Ré Dó♯
m[19] = [(NOTE_D4, 1), (NOTE_D4, 1), (NOTE_E4, 1)]                          # Ré Ré Mi
m[20] = [(NOTE_F4, 1), (NOTE_F4, 1), (NOTE_G4, 1)]                          # Fá Fá Sol
m[21] = [(NOTE_A4, .5), (NOTE_F4, .5), (R, 1), (NOTE_F4, .5), (NOTE_D4, .5)]   # Lá Fá (pausa) Fá Ré
m[22] = [(NOTE_A3, .5), (R, 2.5)]                                           # Lá grave (pausa)
m[23] = [(NOTE_BB4, .5), (R, 1.5), (NOTE_G4, .5), (NOTE_D4, .5)]            # Si♭ (pausa) Sol Ré
m[24] = [(NOTE_BB3, .5), (R, 2.5)]                                          # Si♭ grave (pausa)
m[25] = [(NOTE_E4, .5), (NOTE_E4, 1), (NOTE_D4, 1.5)]                       # Mi Mi Ré (dim.)
m[26] = [(NOTE_CS4, 1.5), (R, .5), (NOTE_F4, .5), (NOTE_G4, .5)]            # Dó♯ (pausa) Fá Sol

# ---- Parte B (c. 27-34) ----
m[27] = [(NOTE_A4, 1), (NOTE_A4, 1), (NOTE_A4, 1)]                          # Lá Lá Lá
m[28] = [(NOTE_BB4, .5), (NOTE_A4, .5), (R, 2)]                             # Si♭ Lá (pausa)
m[29] = [(NOTE_G4, 1), (NOTE_G4, 1), (NOTE_G4, 1)]                          # Sol Sol Sol
m[30] = [(NOTE_G4, .5), (NOTE_A4, 1), (R, 1.5)]                             # Sol Lá (pausa)
m[31] = m[27]
m[32] = m[28]
m[33] = [(NOTE_G4, 1), (NOTE_F4, 1), (NOTE_E4, 1)]                          # Sol Fá Mi
m[34] = [(NOTE_D4, 1), (R, 1), (NOTE_D4, .5), (NOTE_E4, .5)]                # Ré (pausa) Ré Mi

# ---- Parte C (c. 35-51) ----
m[35] = [(NOTE_F4, 2), (NOTE_G4, .5), (NOTE_A4, .5)]                        # Fá (mínima) Sol Lá
m[36] = [(NOTE_G4, 1), (NOTE_F4, 1), (NOTE_E4, 1)]                          # Sol Fá Mi
m[37] = [(NOTE_F4, 1), (NOTE_G4, 1), (NOTE_A4, 1)]                          # Fá Sol Lá
m[38] = [(NOTE_G4, 2), (NOTE_F4, .5), (NOTE_G4, .5)]                        # Sol (mínima) Fá Sol
m[39] = [(NOTE_A4, 2), (NOTE_G4, .5), (NOTE_F4, .5)]                        # Lá (mínima) Sol Fá
m[40] = [(NOTE_E4, 1), (NOTE_F4, 1), (NOTE_E4, 1)]                          # Mi Fá Mi
m[41] = [(NOTE_D4, 2), (NOTE_E4, .5), (NOTE_CS4, .5)]                       # Ré (mínima) Mi Dó♯
m[42] = m[34]                                                               # Ré (pausa) Ré Mi
m[43] = [(NOTE_F4, 1), (R, 1), (NOTE_E4, .5), (NOTE_F4, .5)]                # Fá (pausa) Mi Fá
m[44] = [(NOTE_G4, 1), (NOTE_F4, 1), (NOTE_G4, 1)]                          # Sol Fá Sol
m[45] = [(NOTE_A4, 1), (NOTE_G4, 1), (NOTE_F4, 1)]                          # Lá Sol Fá
m[46] = m[34]                                                               # Ré (pausa) Ré Mi
m[47] = m[37]                                                               # Fá Sol Lá
m[48] = [(NOTE_BB4, 1), (NOTE_D4, 1), (NOTE_G4, 1)]                         # Si♭ Ré Sol
m[49] = [(NOTE_F4, 1), (R, 1), (NOTE_G4, .5), (NOTE_E4, .5)]                # Fá (pausa) Sol Mi
m[50] = [(NOTE_D4, 1), (R, 1), (NOTE_E4, .5), (NOTE_CS4, .5)]               # Ré (pausa) Mi Dó♯
m[51] = m[9]                                                                # Ré (pausa) Lá Dó

# ---- FINAL (c. 52-67): volta o tema ----
m[52] = m[2]
m[53] = m[3]
m[54] = m[4]
m[55] = m[5]
m[56] = m[2]
m[57] = m[3]
m[58] = m[4]
m[59] = m[9]
m[60] = m[10]
m[61] = m[11]
m[62] = m[12]
m[63] = m[13]
m[64] = m[14]
m[65] = m[15]
m[66] = m[18]                                                               # Mi Mi Ré Dó♯
m[67] = [(NOTE_D4, 3)]                                                      # Ré (final)


# ======================================================================
# MÃO ESQUERDA (baixo), compasso a compasso
# Quase todo compasso é uma única nota longa (semínima pontuada = 3 tempos).
# ======================================================================
b = {}
b[1] = [(R, 1)]                                   # anacruse: pausa
for c in (2, 5, 9, 10, 13, 15, 19, 20, 21, 22, 34, 35, 41, 42, 43, 47, 49, 50, 51, 52, 55, 59, 60, 63, 65, 67):
    b[c] = [(NOTE_D3, 3)]                         # Ré
for c in (3, 6, 11, 14, 46, 53, 56, 61, 64):
    b[c] = [(NOTE_BB2, 3)]                        # Si♭
for c in (4, 16, 18, 25, 26, 33, 40, 54, 66):
    b[c] = [(NOTE_A2, 3)]                         # Lá
for c in (7, 30, 37, 39, 45, 57):
    b[c] = [(NOTE_F2, 3)]                         # Fá
for c in (8, 29, 36, 38, 44, 58):
    b[c] = [(NOTE_C3, 3)]                         # Dó
for c in (12, 23, 24, 48, 62):
    b[c] = [(NOTE_G2, 3)]                         # Sol
b[17] = [(NOTE_A2, 2), (R, 1)]                    # casa 1: Lá (mínima) + pausa
b[27] = [L(NOTE_D3, 3)]                           # Ré ligado ao compasso 28
b[28] = [(NOTE_D3, 3)]
b[31] = [L(NOTE_D3, 3)]                           # Ré ligado ao compasso 32
b[32] = [(NOTE_D3, 3)]


# ======================================================================
# Ordem em que os compassos tocam (anacruse + ritornelo com casa 1 e casa 2)
# ======================================================================
TEMA = list(range(2, 16))                         # c. 2-15 (repetidos no ritornelo)
COMPASSOS = (
    [1]                                           # anacruse
    + TEMA + [16, 17]                             # 1ª vez: tema + casa 1 (volta ao c. 2)
    + TEMA + list(range(18, 68))                  # 2ª vez: tema, pula a casa 1 e segue pela casa 2 até o fim
)


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
try:
    vez = 0
    while REPETICOES == 0 or vez < REPETICOES:
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
        vez += 1
except KeyboardInterrupt:
    print("Parado.")
finally:
    arduino.close()
print("Fim da música!")
