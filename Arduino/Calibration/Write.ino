#include <i2cmaster.h>

int dev =  0x00;
int version = 0;

void setup() {
    i2c_init();
    PORTC = (1 << PORTC4) | (1 << PORTC5);
    I2CWrite(0x25,0xB4,0xB7,0x94);
}

void loop() {
}

void I2CWrite(int adress, unsigned int LSB, unsigned int MSB, int PEC){
    i2c_start_wait(dev+I2C_WRITE);
    i2c_write(adress);
    i2c_write(LSB);
    i2c_write(MSB);
    i2c_write(PEC);
    i2c_stop();
    delay(100);
}
