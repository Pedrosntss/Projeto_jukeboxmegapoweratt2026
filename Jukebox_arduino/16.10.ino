#include <Tone.h>

const int buzzerMelodia = 5; // Pino do Buzzer 1 (Melodia)
const int buzzerBaixo = 6;   // Pino do Buzzer 2 (Baixo)

Tone toneMelodia;
Tone toneBaixo;

void setup() {
  Serial.begin(9600);
  toneMelodia.begin(buzzerMelodia);
  toneBaixo.begin(buzzerBaixo);
}

void loop() {
  if (Serial.available() > 0) {
    String dados = Serial.readStringUntil('\n');

    int freqMelodia, freqBaixo, duracaoTotal;
    int lidos = sscanf(dados.c_str(), "%d %d %d", &freqMelodia, &freqBaixo, &duracaoTotal);

    if (lidos == 3) {
      if (freqMelodia > 0) toneMelodia.play(freqMelodia, duracaoTotal);  // 0 = pausa
      if (freqBaixo > 0) toneBaixo.play(freqBaixo, duracaoTotal);

      delay(duracaoTotal);   // espera o acorde acabar
      delay(30);             // silêncio curto para separar as notas
      Serial.println("OK");  // avisa o Python que pode mandar o próximo
    }
  }
}