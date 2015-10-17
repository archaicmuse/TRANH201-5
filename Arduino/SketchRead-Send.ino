//Prototype de code pour recevoir une valeur analogique d'un pin et l'envoyer à un ordinateur par USB

const int analogPin = A0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  unsigned int sensorValue = analogRead(analogPin); //extreme values can be modified https://www.arduino.cc/en/Reference/AnalogReference
  Serial.write(sensorValue);                        //single-byte data sent by USB

  delay(300);                                       //300ms of delay for additional stability

}
