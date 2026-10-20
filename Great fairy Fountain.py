import serial
import time

PORTA = 'COM3'  # Linux: "/dev/ttyACM0" | Mac: "/dev/cu.usbmodemXXXX"


# Frequências das notas, em Hz
NOTE_REST = 0

NOTE_C3 = 131
NOTE_E3 = 165
NOTE_F3 = 175
NOTE_G3 = 196
NOTE_A3 = 220
NOTE_AS3= 233   # Si bemol 3

NOTE_C4 = 262
NOTE_D4 = 294
NOTE_DS4= 311   # Mi bemol 4
NOTE_E4 = 330
NOTE_F4 = 349
NOTE_FS4= 370
NOTE_G4 = 392
NOTE_A4 = 440
NOTE_AS4= 466   # Si bemol 4
NOTE_C5 = 523
NOTE_CS5= 554   # Ré bemol 5
NOTE_D5 = 587
NOTE_DS5= 622   # Mi bemol 5
NOTE_E5 = 659
NOTE_F5 = 698
NOTE_FS5= 740
NOTE_G5 = 784
NOTE_A5 = 880
NOTE_AS5= 932   # Si bemol 5
NOTE_C6 = 1047

R = NOTE_REST

# ---------- Oitava (ajuste fino, igual ao outro código) ----------
#   1 = como está escrito abaixo | 2 = sobe 1 oitava | 0.5 = desce 1 oitava
MULT_MELODIA = 1
MULT_BAIXO   = 1

# ---------- Andamento (compasso 4/4, "Tranquillo") ----------
# A partitura não diz o BPM; 80 BPM soa tranquilo. Mexa só no BEAT_MS.
BEAT_MS = 750               # 1 tempo (semínima) em ms -> 80 BPM
S = BEAT_MS / 4             # semicolcheia (1/4 de tempo)


def oitava(mao, fator):
    """Multiplica as frequências de uma mão (usado para o 8va)."""
    return [(nota * fator, dur) for nota, dur in mao]


def juntar(melodia, baixo):
    """Junta mão direita e mão esquerda em (melodia, baixo, duracao),
    quebrando as notas longas onde a outra mão muda de nota."""
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
# COMPASSO 1 - introdução: acordes arpejados em tercinas, com "accel."
# O buzzer toca só a nota de cima de cada acorde.
# O baixo (clave de Fá: C3 E3 G3 | Bb3 D4 E4) já está 1 oitava acima,
# igual ao resto do baixo da música.
# ======================================================================
T = BEAT_MS * 2 / 3                          # cada acorde = 2/3 de tempo
accel = [1.15, 1.10, 1.00, 0.95, 0.90, 0.90] # vai acelerando (soma = 6)
topo_intro  = [NOTE_E4, NOTE_G4, NOTE_AS4, NOTE_C5, NOTE_D5, NOTE_E5]
baixo_intro = [NOTE_C4, NOTE_E4, NOTE_G4, NOTE_AS4, NOTE_D5, NOTE_E5]
intro = [(m, b, T * f) for m, b, f in zip(topo_intro, baixo_intro, accel)]


# ======================================================================
# COMPASSOS 2 a 9 - "a tempo", tudo em semicolcheias
# Melodia: escrita com 8va -> soa 1 oitava acima (oitava(..., 2) abaixo)
# Baixo:   escrito com 8vb -> deixei na altura escrita, porque o buzzer
#          soa fraco no grave (é o mesmo truque do MULT_BAIXO = 2 de antes)
# ======================================================================
def arp(*notas):            # grupo de 4 semicolcheias
    return [(n, S) for n in notas]

def base(a, b, c, d, *resto):
    # 3 semicolcheias + 1 ligada à semínima (tempos 1-2), depois 8 semicolcheias
    return [(a, S), (b, S), (c, S), (d, 5 * S)] + [(n, S) for n in resto]

# ---- Mão direita ----
m2 = arp(NOTE_A5, NOTE_D5, NOTE_AS4, NOTE_G4) + arp(NOTE_G5, NOTE_D5, NOTE_AS4, NOTE_G4) + \
     arp(NOTE_FS5, NOTE_D5, NOTE_AS4, NOTE_G4) + arp(NOTE_G5, NOTE_D5, NOTE_AS4, NOTE_G4)
m3 = arp(NOTE_G5, NOTE_C5, NOTE_A4, NOTE_F4) + arp(NOTE_F5, NOTE_C5, NOTE_A4, NOTE_F4) + \
     arp(NOTE_E5, NOTE_C5, NOTE_A4, NOTE_F4) + arp(NOTE_F5, NOTE_C5, NOTE_A4, NOTE_F4)
m4 = arp(NOTE_F5, NOTE_AS4, NOTE_G4, NOTE_E4) + arp(NOTE_E5, NOTE_AS4, NOTE_G4, NOTE_E4) + \
     arp(NOTE_DS5, NOTE_AS4, NOTE_G4, NOTE_E4) + arp(NOTE_E5, NOTE_AS4, NOTE_G4, NOTE_E4)
m5 = arp(NOTE_E5, NOTE_A4, NOTE_F4, NOTE_D4) + arp(NOTE_D5, NOTE_A4, NOTE_F4, NOTE_D4) + \
     arp(NOTE_CS5, NOTE_A4, NOTE_F4, NOTE_D4) + arp(NOTE_D5, NOTE_A4, NOTE_F4, NOTE_D4)
m6 = m2
m7 = arp(NOTE_G5, NOTE_DS5, NOTE_C5, NOTE_A4) + arp(NOTE_G5, NOTE_DS5, NOTE_C5, NOTE_A4) + \
     arp(NOTE_FS5, NOTE_DS5, NOTE_C5, NOTE_A4) + arp(NOTE_FS5, NOTE_DS5, NOTE_C5, NOTE_A4)
m8 = arp(NOTE_C6, NOTE_D5, NOTE_AS4, NOTE_G4) + arp(NOTE_AS5, NOTE_D5, NOTE_AS4, NOTE_G4) + \
     arp(NOTE_A5, NOTE_D5, NOTE_AS4, NOTE_G4) + arp(NOTE_AS5, NOTE_D5, NOTE_AS4, NOTE_G4)
m9 = arp(NOTE_A5, NOTE_D5, NOTE_AS4, NOTE_E4) + arp(NOTE_G5, NOTE_D5, NOTE_AS4, NOTE_E4) + \
     arp(NOTE_F5, NOTE_D5, NOTE_AS4, NOTE_E4) + arp(NOTE_E5, NOTE_D5, NOTE_AS4, NOTE_E4)

# ---- Mão esquerda ----
b2 = base(NOTE_G3, NOTE_AS3, NOTE_D4, NOTE_G4,
          NOTE_D4, NOTE_G4, NOTE_AS4, NOTE_D5,  NOTE_D5, NOTE_AS4, NOTE_G4, NOTE_D4)
b3 = base(NOTE_F3, NOTE_A3, NOTE_C4, NOTE_F4,
          NOTE_C4, NOTE_F4, NOTE_A4, NOTE_C5,   NOTE_C5, NOTE_A4, NOTE_F4, NOTE_C4)
b4 = base(NOTE_C4, NOTE_E4, NOTE_G4, NOTE_E4,
          NOTE_C4, NOTE_G4, NOTE_AS4, NOTE_C5,  NOTE_AS4, NOTE_G4, NOTE_E4, NOTE_C4)
b5 = base(NOTE_D4, NOTE_F4, NOTE_A4, NOTE_F4,
          NOTE_D4, NOTE_A4, NOTE_C5, NOTE_D5,   NOTE_C5, NOTE_A4, NOTE_FS4, NOTE_D4)
b6 = b2
b7 = base(NOTE_A3, NOTE_C4, NOTE_DS4, NOTE_A4,
          NOTE_D4, NOTE_FS4, NOTE_A4, NOTE_C5,  NOTE_DS5, NOTE_D5, NOTE_C5, NOTE_A4)
b8 = b2
b9 = base(NOTE_C4, NOTE_E4, NOTE_G4, NOTE_AS4,
          NOTE_C4, NOTE_E4, NOTE_G4, NOTE_AS4,  NOTE_C5, NOTE_AS4, NOTE_G4, NOTE_E4)

mao_direita  = oitava(m2 + m3 + m4 + m5 + m6 + m7 + m8 + m9, 2)   # 8va
mao_esquerda = b2 + b3 + b4 + b5 + b6 + b7 + b8 + b9

parte = juntar(mao_direita, mao_esquerda)

# ---- Ordem: compasso 1 uma vez, depois 2-9 com o sinal de repetição ----
partitura = intro + parte + parte

melodyNotes   = tuple(n[0] for n in partitura)
bassNotes     = tuple(n[1] for n in partitura)
noteDurations = tuple(n[2] for n in partitura)


print("Conectando ao Arduino...")
arduino = serial.Serial(PORTA, 9600, timeout=5)
time.sleep(2)
print("Conectado! Tocando música...")

for i in range(len(melodyNotes)):
    freq_m = int(melodyNotes[i] * MULT_MELODIA)
    freq_b = int(bassNotes[i] * MULT_BAIXO)
    duracao = int(noteDurations[i])

    comando = f"{freq_m} {freq_b} {duracao}\n"
    arduino.write(comando.encode('utf-8'))

    resposta = arduino.readline()
    if not resposta:
        print("Arduino não respondeu na nota", i)

arduino.close()
print("Fim da música!")
