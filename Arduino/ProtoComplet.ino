#include <AccelStepper.h>
#include <SD.h>
#include <SPI.h>

File myDATA;
byte resolutionX = 80;
byte resolutionY = 80;
const int analogPin = A0;
AccelStepper Xaxis(1, 3, 6);
AccelStepper Yaxis(1, 4, 7);


void setup(){
  Serial.begin(9600);
  while (!Serial) {;}
  SD.begin();
  stepsDisplacement(0,0);
}

void stepsDisplacement(byte x, byte y){
  Xaxis.moveTo(x);
  Xaxis.runToPosition();
  Yaxis.moveTo(y);                  
  Yaxis.runToPosition();
}

void dataManagement(int value){
  myDATA.println(value);
  myDATA.println("\n");
  Serial.write(value);
}

void loop(){
  stepsDisplacement((byte)(-0.5)*resolutionX, (byte)0.5*resolutionY);
  myDATA = SD.open("data.txt", FILE_WRITE); 
  dataManagement(resolutionX);
  
  for(byte yi = 1; yi =< resolutionY; yi++) {
    dataManagement((int)analogRead(analogPin));  

    short int direction = pow(-1, yi % 2);
    for(byte xi = 1; xi =< resolutionX; xi++){
      Xaxis.move(-1*direction);
      Xaxis.runToPosition();
      dataManagement((int)analogRead(analogPin));
    }
    Yaxis.move(-1);
    Yaxis.runToPosition();
  }
  myDATA.close();
  stepsDisplacement(0,0);
  delay(3600000);
}

