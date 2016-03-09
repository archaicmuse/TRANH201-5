#include <Wire.h>
#include <Adafruit_MLX90614.h>
#include <Servo.h>

byte resolutionX = 80;
byte resolutionY = 80;
byte xTop = 90 - resolutionX/2;
byte yTop = 90 + resolutionY/2;
Adafruit_MLX90614 mlx = Adafruit_MLX90614();
Servo ServoX;
Servo ServoY;

void setup(){
  Serial.begin(9600);
  mlx.begin();
  ServoX.attach(10);
  ServoY.attach(9);
}

void loop(){
  if(Serial.available() > 0){
    ServoX.write(xTop);
    ServoY.write(yTop);
    for(byte yi = yTop; yi > yTop - resolutionY; yi--){
      short int direction = -1*pow(-1, yi % 2);
      ServoY.write(yi);
      if(direction == 1){
        for(byte xi = xTop; xi < xTop + resolutionX; xi++){
          ServoX.write(xi);
          delay(20);
          Serial.println(mlx.readObjectTempC());
          
        }
      } else {
        for(byte xi = xTop + resolutionX; xi > xTop; xi--){
          ServoY.write(xi);
          delay(20);
          Serial.println(mlx.readObjectTempC());
        }
      }
    }
    ServoX.write(90);
    ServoY.write(90);
    exit(0);
  }
}
