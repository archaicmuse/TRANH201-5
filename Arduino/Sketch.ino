#include <Servo.h>
#include <Wire.h>
#include <Adafruit_MLX90614.h>

byte resolutionX = 80;
byte resolutionY = 80;

Adafruit_MLX90614 mlx = Adafruit_MLX90614();
Servo servoX;
Servo servoY;

void setup(){
  Serial.begin(9600);
  mlx.begin(); 
  servoX.attach(9);
  servoY.attach(10);
}

void loop(){
  if (Serial.available() > 0) {
    for(byte yi = 0; yi < resolutionY; yi++) {
      Serial.print(mlx.readObjectTempC());
      short int direction = -1*pow(-1, yi%2);
      for(byte xi = 0, xi < resolutionX; xi++){
        servoX.write((byte)(-0.5)*resolutionX*direction + direction*xi + 0.5*(direction - 1) + 90);
        delay(20);
        Serial.print(mlx.readObjectTempC());
      }
      servoY.write((byte)0.5*resolutionY - yi + 90);
      delay(20);
    }
    servoX.write(90);
    servoY.write(90);
    exit(0);
  }
}
