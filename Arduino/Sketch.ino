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
  byte xi = 0;
  for(byte yi = 0; yi < resolution; yi++) {
    Serial.print(mlx.readObjectTempC());
    short int direction = pow(-1, yi%2);
    for(xi, xi < resolution; xi++){
      servoX.write((byte)(-0.5)*resolutionX + direction + 90);
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

