#include <i2cmaster.h>

int dev =  0x00;
int version = 0;

unsigned int I2CRead(int adress){
        i2c_start_wait(dev+I2C_WRITE);
        i2c_write(adress);
        i2c_rep_start(dev+I2C_READ);
        unsigned int LSB = i2c_readAck();
        unsigned int MSB = i2c_readAck();
        unsigned int pec = i2c_readNak();
        i2c_stop();
        unsigned int regValue = (((MSB) << 8) + LSB);
        return regValue;
        delay(100);
}

void setup()
{
        //Make sure you set the Baudrate inside the Serial Window to 9600
        Serial.begin(9600);
        Serial.println("This program will read the EEPROM settings of your sensor");
        Serial.println("");
        Serial.println("PLEASE NOTE DOWN CAREFULLY THE FOLLOWING VALUES !");
        Serial.println("");

        //Initialising the I2C Bus and activating the internal pullup resistors
        i2c_init();
        PORTC = (1 << PORTC4) | (1 << PORTC5);

        //Reading the previous values
        Serial.print("Filter settings: ");
        Serial.println(I2CRead(0x25));

        Serial.print("Maximum temp: ");
        Serial.println(I2CRead(0x20));

        Serial.print("Minimum temp: ");
        Serial.println(I2CRead(0x21));
}


void loop()
{
}
