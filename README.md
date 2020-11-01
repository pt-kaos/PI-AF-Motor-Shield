This project is meant to make available similar functions of the Arduino AF-Motor library to the Raspberry Pi so that we can use the old Adafruit Motor Shield V1.


I've copied a lot of constants from the "AF-Motor.h". I left out many that I believe that are not necessary.

There is still some work to do:
- Test Motors 3 & 4
- Review ant test Stepper Motor Class
- Review the GPIO pins used:
	=> Maybe use the 4 PWM GPIO pins for the PWM connectons
	=> Avoid using GPIO pins used for I2C, UART and SPI
- It would be interesting to include a schematic of the connections used and maybe some Python program to run motors, as an example.
