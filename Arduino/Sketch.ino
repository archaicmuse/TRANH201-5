#include <Wire.h>
#include <Adafruit_MLX90614.h>
#include <Servo.h>
#include <SPI.h>
#include <SD.h>

byte resolutionX = 80;
byte resolutionY = 80;
byte xTop = 90 + resolutionX/2;
byte yTop = 90 + resolutionY/2;
String Line;
Adafruit_MLX90614 mlx = Adafruit_MLX90614();
Servo ServoX;
Servo ServoY;
File data;

void setup(){
    Serial.begin(9600);
    mlx.begin();
    ServoX.attach(10);
    ServoY.attach(9);
    pinMode(2, INPUT);
}

void loop(){
    int buttonState = digitalRead(2);
    if(Serial.available() > 0 || buttonState == HIGH) {
        ServoX.write(xTop);
        ServoY.write(yTop);
        if(SD.begin(4)){
            data = SD.open("data.csv", FILE_WRITE);
        }
        for(byte yi = yTop; yi > yTop - resolutionY; yi--) {
            for(byte xi = xTop; xi > xTop - resolutionX; xi--) {
                ServoX.write(ServoX.read() - 1);
                delay(20);
                double temperature = mlx.readObjectTempC();
                Serial.println(temperature);
                Line.concat(String(temperature));
                if (xi != xTop - resolutionX - 1) {
                    Line.concat(",");
                }
            }
            if(SD.begin(4)){
                if(data){
                    data.println(Line);
                    Line = "";
                }
            }
            ServoX.write(xTop);
            ServoY.write(ServoY.read() - 1);
        }
        if(SD.begin(4)){
            data.close();
        }
        ServoX.write(90);
        ServoY.write(90);
        exit(0);
    }
}
