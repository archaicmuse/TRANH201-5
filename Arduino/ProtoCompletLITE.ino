#include <AccelStepper.h>

byte resolutionX = 80;
byte resolutionY = 80;
const int analogPin = A0;
AccelStepper Xaxis(1, 3, 6);
AccelStepper Yaxis(1, 4, 7);

void setup(){
  Serial.begin(9600);
  stepsDisplacement(0,0);
}

void stepsDisplacement(byte x, byte y){
  Xaxis.moveTo(x);
  Xaxis.runToPosition();
  Yaxis.moveTo(y);                  
  Yaxis.runToPosition();
}


void loop(){
  stepsDisplacement((byte)(-0.5)*resolutionX, (byte)0.5*resolutionY);
  byte xi = 0;
  for(byte yi = 0; yi < resolutionY; yi++) {
    Serial.write(xi);
    Serial.write(yi);
    Serial.write((int)analogRead(analogPin));  
    short int direction = pow(-1, yi % 2);
    for(xi; xi < resolutionX; xi++){
      Xaxis.move(direction);
      Xaxis.runToPosition();
      Serial.write(xi);
      Serial.write(yi);
      Serial.write((int)analogRead(analogPin));
    }
    Yaxis.move(-1);
    Yaxis.runToPosition();
  }
  stepsDisplacement(0,0);
  delay(3600000);
}
