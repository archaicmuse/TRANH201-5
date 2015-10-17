//Prototype de stockage de données analogiques sur une carte SD (ou microSD)
//Après écriture, envoi en serial USB

#include <SD.h>
#include <SPI.h>

File myFile;

void setup() {
  
  Serial.begin(9600);
  while (!Serial) {;}                             //wait for serial to connect (native USB only)
  
}

void loop() {
  int dataToWrite = 37;
  myFile = SD.open("data.txt", FILE_WRITE);       //creation or opening or TXT file
  
  for (int i = 0; i<10; i++){
    myFile.println(dataToWrite);            //write data 10*, on a new line each time
    myFile.println("\n");
  }
  
  myFile.close();                                 //close the opened file
  Serial.write(dataToWrite);                      //send data to serial USB too

  while(1) {}

}
