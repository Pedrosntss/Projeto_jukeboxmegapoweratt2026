const int buzzer1 = 2;
const int buzzer2 = 3;

void setup() {
Serial.begin(9600);
pinMode(buzzer1, OUTPUT);
pinMode(buzzer2, OUTPUT);
}

void loop() {
  if (digitalRead(buzzer1) == LOW){
    Serial.print("1");
    delay(300);
  }

  if(digitalRead(buzzer2) == LOW){
    Serial.print("2");
    delay(300);
  }

}
