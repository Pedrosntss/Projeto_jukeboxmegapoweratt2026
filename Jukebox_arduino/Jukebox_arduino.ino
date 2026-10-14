/*
  Ligacoes:
    Buzzer 1 (melodia) -> pino 5
    Buzzer 2 (baixo)   -> pino 6
*/

#define BUZZER_MELODY 5
#define BUZZER_BASS   6

#define NOTE_REST 0

void setup() {
  Serial.begin(9600);
  pinMode(BUZZER_MELODY, OUTPUT);
  pinMode(BUZZER_BASS, OUTPUT);
}

void playDualTone(int pin1, int freq1, int pin2, int freq2, unsigned long duration) {
  unsigned long startTime = millis();

  unsigned long period1 = freq1 > 0 ? 1000000UL / freq1 : 0;
  unsigned long period2 = freq2 > 0 ? 1000000UL / freq2 : 0;

  unsigned long lastChange1 = micros();
  unsigned long lastChange2 = micros();

  bool state1 = LOW;
  bool state2 = LOW;

  while (millis() - startTime < duration) {
    unsigned long now = micros();

    if (period1 > 0 && (now - lastChange1 >= period1 / 2)) {
      state1 = !state1;
      digitalWrite(pin1, state1);
      lastChange1 = now;
    }

    if (period2 > 0 && (now - lastChange2 >= period2 / 2)) {
      state2 = !state2;
      digitalWrite(pin2, state2);
      lastChange2 = now;
    }
  }

  digitalWrite(pin1, LOW);
  digitalWrite(pin2, LOW);
}

void loop(){
arduino.write(tocar_musica)

  delay(5000); // Pausa de 5 segundos ao terminar toda a trilha
}
