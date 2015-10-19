#include <AccelStepper.h>                           //importing the AccelStepper library

byte resolutionX = 80;                              // must be an integer (0-255)
byte resolutionY = 80;

AccelStepper Xaxis(1, 3, 6);                        //steppers initialization (type, step pin, direction pin)
AccelStepper Yaxis(1, 4, 7);

void setup() {
  stepsDisplacement(0,0); 
}

void stepsDisplacement(byte x, byte y){
  Xaxis.moveTo(x);                                  //steppers reset in neutral position
  Xaxis.runToPosition();
  Yaxis.moveTo(y);                  
  Yaxis.runToPosition();
}

void loop(){    
  stepsDisplacement((byte)(-0.5)*resolutionX, (byte)0.5*resolutionY);

  for(byte yi = 1; yi < resolutionY; yi++) {
    //read IR sensor
    short int direction = pow(-1, yi % 2);
    for(byte xi = 1; xi < resolutionX; xi++){
      Xaxis.move(-1*direction);                     //X line movement
      Xaxis.runToPosition();
      //read IR sensor
    }
    Yaxis.move(-1);                                 //Y column movement
    Yaxis.runToPosition();
  }

  stepsDisplacement(0,0);                           // steppers reset in neutral position
  delay(3600000);                                   //one hour pause
}
