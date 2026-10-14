'''
  The Legend of Zelda: Ocarina of Time - Song of Storms
  Arranjo para 2 buzzers PASSIVOS (melodia + baixo), compasso 3/4.

  Ligacoes (cada buzzer: um fio no pino, o outro no GND):
    Buzzer 1 (melodia) -> pino 5
    Buzzer 2 (baixo)   -> pino 6

  Placa: Arduino Uno R3 / Nano (ATmega328P).

  Como funciona: os dois tons sao gerados pelo Timer1, por interrupcao.
  Assim a frequencia fica exata e o loop() so precisa de delay().
  Por isso nao use Servo nem analogWrite() nos pinos 9 e 10 junto com
  este sketch (eles usam o mesmo timer).
'''
import serial
import time

# --- INICIALIZAÇÃO DA PORTA SERIAL ---
# Altere "COM3" para a porta onde o seu Arduino está conectado no Windows!
PORTA_ARDUINO = "COM3" 

try:
    arduino = serial.Serial(PORTA_ARDUINO, 9600, timeout=1)
    time.sleep(2) # Aguarda o Arduino reiniciar após conectar
    print(f"Conectado com sucesso ao Arduino na porta {PORTA_ARDUINO}!")
except Exception as e:
    print(f"ERRO: Não foi possível conectar na porta {PORTA_ARDUINO}. Verifique o número da COM. Detalhes: {e}")
    exit()

BUZZER_MELODY = 5
BUZZER_BASS  = 6

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
MULT_MELODIA = 2
MULT_BAIXO  = 2

# ---------- Andamento (compasso 3/4) ----------
# Para deixar a musica mais rapida/lenta, mexa so no BEAT_MS.
BEAT_MS  = 500                # 1 tempo (seminima) em ms -> 120 BPM
COLCHEIA = (BEAT_MS / 2)      # 1/2 tempo
SEMINIMA = (BEAT_MS)          # 1 tempo
MINIMA   = (BEAT_MS * 2)      # 2 tempos
MINIMA_P = (BEAT_MS * 3)      # 3 tempos (compasso inteiro)

# Silencio entre as notas: 25% da duracao, mas no maximo GAP_MAX_MS
# (evita "buracos" enormes no meio das notas longas)
GAP_RATIO = 0.25
GAP_MAX_MS = 60

# Partitura - Buzzer 1 (Melodia)
melodyNotes = (
  # 1. INTRO (so o baixo toca - 4 compassos)
  NOTE_REST, NOTE_REST, NOTE_REST,
  NOTE_REST, NOTE_REST, NOTE_REST,
  NOTE_REST, NOTE_REST, NOTE_REST,
  NOTE_REST, NOTE_REST, NOTE_REST,

  # 2. TEMA (A)
  NOTE_D4, NOTE_F4, NOTE_D5,                              # compasso 1
  NOTE_D4, NOTE_F4, NOTE_D5,                              # compasso 2
  NOTE_E5, NOTE_F5, NOTE_E5, NOTE_F5, NOTE_E5, NOTE_C5,   # compasso 3
  NOTE_A4,                                                # compasso 4
  NOTE_A4, NOTE_D4, NOTE_F4, NOTE_G4, NOTE_A4,            # compasso 5
  NOTE_A4, NOTE_D4, NOTE_F4, NOTE_G4, NOTE_E4,            # compasso 6

  # 3. TEMA (A - Repeticao)
  NOTE_D4, NOTE_F4, NOTE_D5,
  NOTE_D4, NOTE_F4, NOTE_D5,
  NOTE_E5, NOTE_F5, NOTE_E5, NOTE_F5, NOTE_E5, NOTE_C5,
  NOTE_A4,
  NOTE_A4, NOTE_D4, NOTE_F4, NOTE_G4, NOTE_A4,
  NOTE_A4, NOTE_D4, NOTE_F4, NOTE_G4, NOTE_E4,

  # 4. FINALIZACAO (ultima nota alongada)
  NOTE_D4, NOTE_F4, NOTE_D5
)

# Partitura - Buzzer 2 (Baixo)
bassNotes = (
  # 1. INTRO (D - E - F - E, um compasso para cada nota)
  NOTE_D3, NOTE_D3, NOTE_D3,
  NOTE_E3, NOTE_E3, NOTE_E3,
  NOTE_F3, NOTE_F3, NOTE_F3,
  NOTE_E3, NOTE_E3, NOTE_E3,

  # 2. TEMA (A)
  NOTE_D3, NOTE_D3, NOTE_A3,                              # compasso 1
  NOTE_D3, NOTE_D3, NOTE_A3,                              # compasso 2
  NOTE_A3, NOTE_A3, NOTE_A3, NOTE_A3, NOTE_A3, NOTE_A3,   # compasso 3
  NOTE_D3,                                                # compasso 4
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_G3, NOTE_A3,            # compasso 5
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_G3, NOTE_A3,            # compasso 6

  # 3. TEMA (A - Repeticao)
  NOTE_D3, NOTE_D3, NOTE_A3,
  NOTE_D3, NOTE_D3, NOTE_A3,
  NOTE_A3, NOTE_A3, NOTE_A3, NOTE_A3, NOTE_A3, NOTE_A3,
  NOTE_D3,
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_G3, NOTE_A3,
  NOTE_D3, NOTE_D3, NOTE_D3, NOTE_G3, NOTE_A3,

  # 4. FINALIZACAO (ultima nota alongada)
  NOTE_D3, NOTE_D3, NOTE_D3
)

# Duracoes (ms)
noteDurations = (
  # 1. INTRO (4 compassos de 3 tempos)
  SEMINIMA, SEMINIMA, SEMINIMA,
  SEMINIMA, SEMINIMA, SEMINIMA,
  SEMINIMA, SEMINIMA, SEMINIMA,
  SEMINIMA, SEMINIMA, SEMINIMA,

  # 2. TEMA (A)
  COLCHEIA, COLCHEIA, MINIMA,                                         # compasso 1
  COLCHEIA, COLCHEIA, MINIMA,                                         # compasso 2
  COLCHEIA, COLCHEIA, COLCHEIA, COLCHEIA, COLCHEIA, COLCHEIA,         # compasso 3
  MINIMA_P,                                                           # compasso 4
  COLCHEIA, COLCHEIA, COLCHEIA, COLCHEIA, SEMINIMA,                   # compasso 5
  COLCHEIA, COLCHEIA, COLCHEIA, COLCHEIA, SEMINIMA,                   # compasso 6

  # 3. TEMA (A - Repeticao)
  COLCHEIA, COLCHEIA, MINIMA,
  COLCHEIA, COLCHEIA, MINIMA,
  COLCHEIA, COLCHEIA, COLCHEIA, COLCHEIA, COLCHEIA, COLCHEIA,
  MINIMA_P,
  COLCHEIA, COLCHEIA, COLCHEIA, COLCHEIA, SEMINIMA,
  COLCHEIA, COLCHEIA, COLCHEIA, COLCHEIA, SEMINIMA,

  # 4. FINALIZACAO (ultima nota alongada)
  COLCHEIA, COLCHEIA, MINIMA_P
)

# Garante (na compilacao) que as 3 listas tem o mesmo tamanho
assert len(melodyNotes) == len(noteDurations) == len(bassNotes), \
    "melodyNotes, bassNotes e noteDurations precisam ter o mesmo tamanho!"

totalNotes = len(noteDurations)



# O loop da musica em PYTHON
def tocar_musica ():
  for i in range(totalNotes):
      duration = noteDurations[i]

# Calcula o pequeno silêncio (staccato) entre as notas
      gap = duration * GAP_RATIO
      if gap > GAP_MAX_MS: 
          gap = GAP_MAX_MS
 # 1. Manda o Arduino TOCAR as notas atuais
      freq_m = melodyNotes[i] * MULT_MELODIA
      freq_b = bassNotes[i] * MULT_BAIXO        

 # Envia o comando via Serial (ex: "440,220\n")
      comando_tocar = f"{freq_m},{freq_b}\n"
      arduino.write(comando_tocar.encode())
    
    # Espera o tempo da nota tocar (convertido para segundos)
      time.sleep((duration - gap) / 1000)

    # 2. Manda o Arduino SILENCIAR (o gap entre as notas)
      comando_silencio = f"{NOTE_REST},{NOTE_REST}\n"
      arduino.write(comando_silencio.encode())
    
    # Espera o tempo do gap (convertido para segundos)
      time.sleep(gap / 1000)

  return tocar_musica   



# Pausa de 5 segundos ao terminar toda a trilha
time.sleep(5)

# Fecha a porta serial ao encerrar
arduino.close()