#include <Servo.h>

Servo moteurX;
Servo moteurY;

void setup() {
  moteurX.attach(9);
  moteurY.attach(10);
}


void loop() {
  moteurX.write(90);
  moteurY.write(90);

  moteurX.write(50); 
  moteurY.write(130);

  for(byte i=0; i<80;i++){
    for(byte j=0; j<80;j++){
      if (j%2 == 0){
        moteurX.write(moteurX.read() +1);
      }
      else{
        moteurX.write(moteurX.read() -1);
      }
    }
  moteurY.write(moteurY.read() -1);
  }
}
