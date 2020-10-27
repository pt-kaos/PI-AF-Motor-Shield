import RPi.GPIO as gpio
import time
from time import sleep

MOTOR1 = 1
MOTOR2 = 2
MOTOR3 = 3
MOTOR4 = 4

FORWARD = 1
BACKWARD = 2
BRAKE = 3
RELEASE = 4 # Não utilizo

def BIT(bit): return (1<<(bit))

class Motor():
    latch_state = 0 << 8

    MOTORDATA=10
    MOTORCLK=18
    MOTORLATCH=8
    MOTORENABLE=22

    MOTOR1PWM=26
    MOTOR2PWM=24

            #define MOTOR1_A 2
            #define MOTOR1_B 3
            #define MOTOR2_A 1
            #define MOTOR2_B 4
            #define MOTOR4_A 0   ===> No diagrama este é o 3_A
            #define MOTOR4_B 6   ===> No diagrama este é o 3_B
            #define MOTOR3_A 5   ===> No diagrama este é o 4_A
            #define MOTOR3_B 7   ===> No diagrama este é o 4_B
            # Além disso a ordem aparece trocada (primeiro o 4 e depois o 3???

    M1={'A': 2, 'B': 3}
    M2={'A': 1, 'B': 4}
    M3={'A': 0, 'B': 6}     # Utilizo a numeração do esquema do circuito
    M4={'A': 5, 'B': 7}     # utilizo a numeração do esquema do circuito

    def __init__(self):
        self.setupBoard()
        self.pause=0
        self.latch_state=0
        self.latchTX()

    def setupBoard(self):
        gpio.setup(self.MOTORDATA,gpio.OUT)
        gpio.output(self.MOTORDATA,gpio.LOW)
        gpio.setup(self.MOTORCLK,gpio.OUT)
        gpio.output(self.MOTORCLK,gpio.LOW)
        gpio.setup(self.MOTORLATCH,gpio.OUT)
        gpio.output(self.MOTORLATCH,gpio.HIGH)
        gpio.setup(self.MOTORENABLE,gpio.OUT)
        gpio.output(self.MOTORENABLE,gpio.LOW)
        gpio.setup(self.MOTOR1PWM,gpio.OUT)
        gpio.output(self.MOTOR1PWM,gpio.LOW)
        gpio.setup(self.MOTOR2PWM,gpio.OUT)
        gpio.output(self.MOTOR2PWM,gpio.LOW)
        self.m1_pwm=gpio.PWM(self.MOTOR1PWM, 50)
        self.m2_pwm=gpio.PWM(self.MOTOR2PWM, 50)

    def latchTX(self):
        gpio.output(self.MOTORLATCH, gpio.LOW)
        sleep(self.pause)                             # AUTORECRIAÇÃO
        gpio.output(self.MOTORDATA, gpio.LOW)

        for i in range(8):
            sleep(self.pause)
            gpio.output(self.MOTORCLK, gpio.LOW)
            if(self.latch_state & (1<<(7-i))):
                gpio.output(self.MOTORDATA, gpio.HIGH)
            else:
                gpio.output(self.MOTORDATA, gpio.LOW)
            sleep(self.pause)
            gpio.output(self.MOTORCLK, gpio.HIGH)
        gpio.output(self.MOTORLATCH, gpio.HIGH)

    def DCMotorRun(self, motornum, cmd):
        a = 0
        b = 0

        if (motornum == 1):   a = self.M1['A']; b = self.M1['B']
        elif (motornum == 2): a = self.M2['A']; b = self.M2['B']
        elif (motornum == 3): a = self.M3['A']; b = self.M3['B']
        elif (motornum == 4): a = self.M4['A']; b = self.M4['B']
        else: return;

        if (cmd == FORWARD):
            self.latch_state |=  BIT(a)
            self.latch_state &= ~BIT(b)
        elif (cmd == BACKWARD):
            self.latch_state &= ~BIT(a)
            self.latch_state |=  BIT(b)
#        elif (cmd == BREAK):
#            self.latch_state &=  BIT(a)
#            self.latch_state &=  BIT(b)
        elif (cmd == RELEASE):
            self.latch_state &= ~BIT(a)
            self.latch_state &= ~BIT(b)
        else: return;
        self.latchTX();

    def RunFW(self):
        self.DCMotorRun(MOTOR1, FORWARD) 
        self.DCMotorRun(MOTOR2, FORWARD)
        self.m1_pwm.start(0)
        self.m2_pwm.start(0)
        for i in range(0,101,5):
            self.m1_pwm.ChangeDutyCycle(i)
            self.m2_pwm.ChangeDutyCycle(i)
            sleep(0.1)
        sleep(5)
        for i in range(100,-1,-5):
            self.m1_pwm.ChangeDutyCycle(i)
            self.m2_pwm.ChangeDutyCycle(i)
            sleep(0.1)
        self.DCMotorRun(MOTOR1, RELEASE) 
        self.DCMotorRun(MOTOR2, RELEASE)

#   gpio.cleanup()

if __name__=="__main__":
    main()
