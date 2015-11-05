#include <Servo.h>

byte resolutionX = 80;
byte resolutionY = 80;
const int analogPin = A0;

Servo servoX;
Servo servoY;

void setup(){
  Serial.begin(9600);
  servoX.attach(9);
  servoY.attach(10);
}

void loop(){
  byte xi = 0;
  for(byte yi = 0; yi < resolution; yi++) {
    Serial.write(xi);
    Serial.write(yi);
    Serial.write((int)analogRead(analogPin));
    short int direction = pow(-1, yi%2);
    for(xi, xi < resolution; xi++){
      servoX.write((byte)(-0.5)*resolutionX + direction);
      delay(20);
      Serial.write(xi);
      Serial.write(yi);
      Serial.write((int)analogRead(analogPin));
    }
    servoY.write((byte)0.5*resolutionY - yi);
    delay(20);
  }
  servoX.write(0);
  servoY.write(0);
  delay(36000);
}

