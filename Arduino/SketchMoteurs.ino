#include <AccelStepper.h>                   //importing the AccelStepper library

// const float angularStep = 0.9;
const unsigned short int resolutionX = 80;                       // must be an integer
const unsigned short int resolutionY = 80;

AccelStepper Xaxis(1, 3, 6);                 //steppers initialization (type, step pin, direction pin)
AccelStepper Yaxis(1, 4, 7);

void setup() {
    
  Xaxis.moveTo(0);                            //steppers reset in neutral position
  Xaxis.runToPosition();
  Yaxis.moveTo(0);                  
  Yaxis.runToPosition(); 
}

void loop(){    
  
  Xaxis.moveTo((int)(-0.5)*resolutionX);      //initial X displacement instruction(extreme left, cut)
  Xaxis.runToPosition();                      //instruction process
  Yaxis.moveTo((int)0.5*resolutionY);         //initial Y displacement instruction (extreme high, cut)
  Yaxis.runToPosition();                      //instruction process

  for(int yi = 1; yi <= resolutionY; yi++) {
    //read IR sensor
    short int direction = pow(-1, yi % 2);
    for(int xi = 1; xi <= resolutionX; xi++){
      Xaxis.moveTo(Xaxis.currentPosition() - direction); //X line movement
      Xaxis.runToPosition();

      //read IR sensor
    }
    
    Yaxis.moveTo(Yaxis.currentPosition() -1); //Y column movement
    Yaxis.runToPosition();
  }

  Xaxis.moveTo(0);                          // steppers reset in neutral position
  Xaxis.runToPosition();
  Yaxis.moveTo(0);                  
  Yaxis.runToPosition();        
}

