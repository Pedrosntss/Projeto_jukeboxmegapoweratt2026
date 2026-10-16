const int buzzerMelodia = 8; // Pino do Buzzer 1
const int buzzerBaixo = 9;   // Pino do Buzzer 2

void setup() {
  Serial.begin(9600);
  pinMode(buzzerMelodia, OUTPUT);
  pinMode(buzzerBaixo, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    String dados = Serial.readStringUntil('\n');
    dados.trim();
    
    // Agora esperamos: "FreqMelodia,FreqBaixo,DuracaoTotal" (Ex: "523,131,300")
    int primeiraVirgula = dados.indexOf(',');
    int segundaVirgula = dados.indexOf(',', primeiraVirgula + 1);
    
    if (primeiraVirgula > 0 && segundaVirgula > 0) {
      int freqMelodia = dados.substring(0, primeiraVirgula).toInt();
      int freqBaixo = dados.substring(primeiraVirgula + 1, segundaVirgula).toInt();
      int duracaoTotal = dados.substring(segundaVirgula + 1).toInt();
      
      // CHAMA A FUNÇÃO DE ARPEJO LOCAL NO ARDUINO
      tocarArpejo(freqMelodia, freqBaixo, duracaoTotal);
      
      // Avisa o Python que o acorde inteiro terminou
      Serial.println("OK");
    }
  }
}

// Função que faz o arpejo rapidinho direto no hardware do Arduino
void tocarArpejo(int fMelodia, int fBaixo, int tempoTotal) {
  // Quantos "passos" de 50 microssegundos cada buzzer espera antes de inverter
  int metadeMelodia = 10000 / fMelodia;
  int metadeBaixo = 10000 / fBaixo;

  int contadorMelodia = 0;
  int contadorBaixo = 0;
  int estadoMelodia = LOW;
  int estadoBaixo = LOW;

  for (int ms = 0; ms < tempoTotal; ms++) {   // cada volta = 1 milissegundo
    for (int t = 0; t < 20; t++) {            // 20 passos de 50 µs = 1 ms

      contadorMelodia++;
      contadorBaixo++;

      // Hora de inverter o buzzer da melodia?
      if (contadorMelodia >= metadeMelodia) {
        if (estadoMelodia == LOW) estadoMelodia = HIGH;
        else estadoMelodia = LOW;
        digitalWrite(buzzerMelodia, estadoMelodia);
        contadorMelodia = 0;
      }

      // Hora de inverter o buzzer do baixo?
      if (contadorBaixo >= metadeBaixo) {
        if (estadoBaixo == LOW) estadoBaixo = HIGH;
        else estadoBaixo = LOW;
        digitalWrite(buzzerBaixo, estadoBaixo);
        contadorBaixo = 0;
      }

      delayMicroseconds(40); // 40 e não 50, pois o resto do código também gasta tempo
    }
  }

  // Desliga os dois
  digitalWrite(buzzerMelodia, LOW);
  digitalWrite(buzzerBaixo, LOW);
  delay(30); // pausa curta entre os acordes
}