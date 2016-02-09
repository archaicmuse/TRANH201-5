#include <Servo.h>
#include <Wire.h>
#include <Adafruit_MLX90614.h>
#include <LiquidCrystal.h>

byte resolutionX = 80;
byte resolutionY = 80;
int progress = 0;

Adafruit_MLX90614 mlx = Adafruit_MLX90614();
Servo servoX;
Servo servoY;
LiquidCrystal lcd(4, 6, 10, 11, 12, 13);

void setup(){
  Serial.begin(9600);
  mlx.begin(); 
  servoX.attach(8);
  servoY.attach(9);
  lcd.begin(16, 2);
}

void loop(){
  if (Serial.available() > 0) {
    lcd.setCursor(15,0);
    lcd.scrollDisplayLeft();
    lcd.print("Welcome here!");
    lcd.setCursor(15,1);
    for(byte yi = 0; yi < resolutionY; yi++) {
      Serial.print(mlx.readObjectTempC());
      short int direction = -1*pow(-1, yi%2);
      for(byte xi = 0; xi < resolutionX; xi++){
        progress = (int) yi/(resolutionY)*100;  
        lcd.scrollDisplayLeft();
        lcd.print("Working" + progress);// need to be converted to string :p
        servoX.write((byte)(-0.5)*resolutionX*direction + direction*xi + 0.5*(direction - 1) + 90);
        delay(20);
        Serial.print(mlx.readObjectTempC());
      }
      servoY.write((byte)0.5*resolutionY - yi + 90);
      delay(20);
    }
    delay(200);
    servoX.write(90);
    servoY.write(90);
    lcd.clear();
    exit(0);
  }
}
