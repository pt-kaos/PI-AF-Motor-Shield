import RPi.GPIO as gpio
import time
from time import sleep


# To create a PWM instance:
# p = GPIO.PWM(channel, frequency)
# To start PWM:
# p.start(dc)   # where dc is the duty cycle (0.0 <= dc <= 100.0)
#
# To change the frequency:
# p.ChangeFrequency(freq)   # where freq is the new frequency in Hz
#
# To change the duty cycle:
# p.ChangeDutyCycle(dc)  # where 0.0 <= dc <= 100.0
# To stop PWM:
# p.stop()


MOTOR12_64KHZ = 64000   # Frequency in Hz
MOTOR12_39KHZ = 39000   # Frequency in Hz
MOTOR34_64KHZ = 64000   # Frequency in Hz
MOTOR34_39KHZ = 39000   # Frequency in Hz

# PWM rate for DC motors.
DC_MOTOR_PWM_FREQ = MOTOR34_64KHZ

# PWM rate for DC motors.
STEPPER1_PWM_RATE = MOTOR12_39KHZ
STEPPER2_PWM_RATE = MOTOR34_39KHZ

MICROSTEPS = 16
microstepcurve=[0, 25, 50, 74, 98, 120, 141, 162, 180, 197, 212, 225, 236, 244, 250, 253, 255]

MOTOR1 = 1
MOTOR2 = 2
MOTOR3 = 3
MOTOR4 = 4

FORWARD = 1
BACKWARD = 2
BRAKE = 3       # Não utilizo
RELEASE = 4

# Constants that the user passes in to the stepper calls
SINGLE = 1
DOUBLE = 2
INTERLEAVE = 3
MICROSTEP = 4

# RPI Pins Used to interface to 74HCT595 of the AF Motor Shield
# Have to change to map GPIO available pins
MOTORLATCH = 8
MOTORDATA = 10
MOTORCLK = 18
MOTORENABLE = 22

# HW PWM phisical pins 12, 13, 18, 19
# SW PWM any pins
MOTOR1PWM = 26
MOTOR2PWM = 24
#MOTOR3PWM = 12
#MOTOR4PWM = 16

M1={'A': 2, 'B': 3}
M2={'A': 1, 'B': 4}
# There is a mismatch between the schematich and the AF-Motor.h
# I use the schemetic numbering for Motor 3 and Motor 4, until I test it.
M3={'A': 0, 'B': 6}
M4={'A': 5, 'B': 7}

latch_state = 0

gpio.setmode(gpio.BOARD)

#def BIT(bit): return (1 << (bit))
def BV(bit): return (1 << (bit))

def initPWM1():
    gpio.setup(MOTOR1PWM,gpio.OUT)
    gpio.output(MOTOR1PWM,gpio.LOW)

def setPWM1(freq):
    gpio.PWM(MOTOR1PWM, freq)

def initPWM2():
    gpio.setup(MOTOR2PWM,gpio.OUT)
    gpio.output(MOTOR2PWM,gpio.LOW)

def setPWM2(freq):
    gpio.PWM(MOTOR2PWM, freq)

def initPWM3():
    gpio.setup(MOTOR3PWM,gpio.OUT)
    gpio.output(MOTOR3PWM,gpio.LOW)

def setPWM3(freq):
    gpio.PWM(MOTOR3PWM, freq)

def initPWM4():
    gpio.setup(MOTOR4PWM,gpio.OUT)
    gpio.output(MOTOR4PWM,gpio.LOW)

def setPWM4(freq):
    gpio.PWM(MOTOR4PWM, freq)

class AFMotorController:
    global latch_state
#    pause=0

    def __init__(self):
        pass

    def enable(self):
        global latch_sate

        gpio.setup(MOTORDATA,gpio.OUT)
        gpio.output(MOTORDATA,gpio.LOW)
        gpio.setup(MOTORCLK,gpio.OUT)
        gpio.output(MOTORCLK,gpio.LOW)
        gpio.setup(MOTORLATCH,gpio.OUT)
        gpio.output(MOTORLATCH,gpio.HIGH)
        gpio.setup(MOTORENABLE,gpio.OUT)
        gpio.output(MOTORENABLE,gpio.LOW)
        
        latch_state = 0

        self.latch_tx()

        gpio.output(MOTORENABLE,gpio.LOW)


    def latch_tx(self):
        global latch_state

        gpio.output(MOTORLATCH, gpio.LOW)
#        sleep(self.pause)   # Don't see the need for this
        gpio.output(MOTORDATA, gpio.LOW)

        for i in range(8):
#            sleep(self.pause)   # Don't see the need for this
            gpio.output(MOTORCLK, gpio.LOW)
            if(latch_state & BV(7-i)):
                gpio.output(MOTORDATA, gpio.HIGH)
            else:
                gpio.output(MOTORDATA, gpio.LOW)
#            sleep(self.pause)   # Don't see the need for this
            gpio.output(MOTORCLK, gpio.HIGH)
        gpio.output(MOTORLATCH, gpio.HIGH)

MC=AFMotorController()

class AF_DCMotor:
    motornum = 1
    pwmfreq = 0

    def __init__(self, motornum, freq = DC_MOTOR_PWM_FREQ):
        self.motornum = motornum
        self.pwmfreq = freq
        global latch_state

        MC.enable()

        if(motornum==1):
            latch_state &= ~BV(M1['A']) & ~BV(M1['B'])
            MC.latch_tx()
            initPWM1()
        elif (motornum == 2):
            latch_state &= ~BV(M2['A']) & ~BV(M2['B']) 
            MC.latch_tx()
            initPWM2()
        elif (motornum == 3):
            latch_state &= ~BV(M3['A']) & ~BV(M3['B']) 
            MC.latch_tx()
            initPWM3()
        elif (motornum == 4):
            latch_state &= ~BV(M4['A']) & ~BV(M4['B']) 
            MC.latch_tx()
            initPWM4()

    def run(self, cmd):
        a = 0
        b = 0
        global latch_state

        if (self.motornum == 1):   a = M1['A']; b = M1['B']
        elif (self.motornum == 2): a = M2['A']; b = M2['B']
        elif (self.motornum == 3): a = M3['A']; b = M3['B']
        elif (self.motornum == 4): a = M4['A']; b = M4['B']
        else: return;

        if (cmd == FORWARD):
            latch_state |=  BV(a)
            latch_state &= ~BV(b)
        elif (cmd == BACKWARD):
            latch_state &= ~BV(a)
            latch_state |=  BV(b)
        elif (cmd == RELEASE):
            latch_state &= ~BV(a)
            latch_state &= ~BV(b)
        else: return
        MC.latch_tx()

    def setSpeed(self, speed):
        if(self.motornum == 1):
            setPWM1(speed)
        elif(self.motornum == 2):
            setPWM2(speed)
        elif(self.motornum == 3):
            setPWM3(speed)
        elif(self.motornum == 4):
            setPWM4(speed)
 
###########################################################
# Need to Work on this. It hasn't been tested yet
# Neet to understand how the stepper motors work, first
###########################################################

class AF_Stepper:
    refsteps = 0        # Steps per revolution
    steppernum = 0
    usperstep = 0
    steppingcounter = 0
    currentstep = 0

    def __init__(self, steps, num):
        global latch_state

        MC.enable()

        self.revsteps = steps
        self.steppernum = num
        self.currentstep = 0

        if(self.steppernum == 1):
            latch_state &= ~BV(M1['A']) & ~BV(M1['B']) & ~BV(M2['A']) & ~BV(M2['B']) # all motor pins to 0
            self.latch_tx()

            # Enable both H bridges
            gpio.setup(MOTOR1PWM,gpio.OUT)
            gpio.setup(MOTOR2PWM,gpio.OUT)
            gpio.output(MOTOR1PWM,gpio.HIGH)
            gpio.output(MOTOR2PWM,gpio.HIGH)

            # use PWM for microstepping support
#            initPWM1(STEPPER1_PWM_RATE)
#            initPWM2(STEPPER1_PWM_RATE)
            setPWM1(255)
            setPWM2(255)
        elif(self.steppernum == 2):
            latch_state &= ~_BV(MOTOR3_A) & ~_BV(MOTOR3_B) & ~_BV(MOTOR4_A) & ~_BV(MOTOR4_B) # all motor pins to 0
            MC.latch_tx()

            gpio.setup(MOTOR3PWM,gpio.OUT)
            gpio.setup(MOTOR4PWM,gpio.OUT)
            gpio.output(MOTOR3PWM,gpio.HIGH)
            gpio.output(MOTOR4PWM,gpio.HIGH)

            # use PWM for microstepping support
#            initPWM3(STEPPER2_PWM_RATE)
#            initPWM4(STEPPER2_PWM_RATE)
            setPWM3(255)
            setPWM4(255)

    def latch_tx(self):
        global latch_state

        gpio.output(MOTORLATCH, gpio.LOW)
        gpio.output(MOTORDATA, gpio.LOW)

        for i in range(8):
            gpio.output(MOTORCLK, gpio.LOW)
            if(latch_state & BV(7-i)):
                gpio.output(MOTORDATA, gpio.HIGH)
            else:
                gpio.output(MOTORDATA, gpio.LOW)
            gpio.output(MOTORCLK, gpio.HIGH)

    def step(self, steps, direction, style = SINGLE):
        uspers = usperstep
        ret = 0
        if (style == INTERLEAVE):
            uspers /=2
        elif (style == MICROSTEP):
            uspers /= MICROSTEPS 
            steps *= MICROSTEPS
        while (steps-=1):
            ret=onestep(direction, style)
            sleep(uspers/1000)
            steppingcounter += (uspers % 1000)
            if (steppingcounter >=1000):
                sleep(1)
                steppingcounter -= 1000
        if (style == MICROSTEP):
            while ((ret!=0) && (ret != MICROSTEPS)):
                ret = onestep(direction, style)
                delay(uspers/1000)
                steppingcounter += (uspers % 1000)
                if (steppingcounter >= 1000):
                    sleep(1)
                    steppingcounter-=1000

    def setSpeed(self, rpm):
        self.usperstep = 60000000 / (self.revsteps * rpm);
        self.steppingcounter = 0

    def onestep(self, direction, style):
        a=b=c=d=0
        ocra = ocrb = 255;

        if (steppernum == 1):
            a = BV(M1['A'])
            b = BV(M2['A'])
            c = BV(M1['B'])
            d = BV(M2['B'])
        elif (steppernum == 2):
            a = BV(M3['A'])
            b = BV(M4['A'])
            c = BV(M3['B'])
            d = BV(M4['B'])
        else:
            return 0

        # next determine what sort of stepping procedure we're up to
        if (style == SINGLE): 
            if ((currentstep/(MICROSTEPS/2)) % 2): #we're at an odd step, weird
                if (direction == FORWARD):
	            currentstep += MICROSTEPS/2
                else:
	            currentstep -= MICROSTEPS/2
            else:                               # go to the next even step
                if (direction == FORWARD):
	            currentstep += MICROSTEPS
                else:
	            currentstep -= MICROSTEPS
        elif (style == DOUBLE):
            if (! (currentstep/(MICROSTEPS/2) % 2)): # we're at an even step, weird
                if (direction == FORWARD):
	            currentstep += MICROSTEPS/2
                else
	            currentstep -= MICROSTEPS/2
            else:                               # go to the next odd step
                if (direction == FORWARD):
	            currentstep += MICROSTEPS
                else:
	            currentstep -= MICROSTEPS
        elif (style == INTERLEAVE):
            if (direction == FORWARD):
                currentstep += MICROSTEPS/2
            else:
                currentstep -= MICROSTEPS/2
        if (style == MICROSTEP):
            if (direction == FORWARD):
                currentstep++
            else:
                # BACKWARDS
                currentstep--

            currentstep += MICROSTEPS*4
            currentstep %= MICROSTEPS*4

            ocra = ocrb = 0

            if ( (currentstep >= 0) && (currentstep < MICROSTEPS)):
                ocra = microstepcurve[MICROSTEPS - currentstep]
                ocrb = microstepcurve[currentstep]
            elif ((currentstep >= MICROSTEPS) && (currentstep < MICROSTEPS*2)):
                ocra = microstepcurve[currentstep - MICROSTEPS]
                ocrb = microstepcurve[MICROSTEPS*2 - currentstep]
            elif ((currentstep >= MICROSTEPS*2) && (currentstep < MICROSTEPS*3)):
                ocra = microstepcurve[MICROSTEPS*3 - currentstep]
                ocrb = microstepcurve[currentstep - MICROSTEPS*2]
            elif ((currentstep >= MICROSTEPS*3) && (currentstep < MICROSTEPS*4)):
                ocra = microstepcurve[currentstep - MICROSTEPS*3]
                ocrb = microstepcurve[MICROSTEPS*4 - currentstep]

        currentstep += MICROSTEPS*4
        currentstep %= MICROSTEPS*4

        if (steppernum == 1):
            setPWM1(ocra)
            setPWM2(ocrb)
        elif (steppernum == 2):
            setPWM3(ocra)
            setPWM4(ocrb)


        # release all
        latch_state &= ~a & ~b & ~c & ~d; # all motor pins to 0

        if (style == MICROSTEP):
            if ((currentstep >= 0) && (currentstep < MICROSTEPS)):
                latch_state |= a | b
            if ((currentstep >= MICROSTEPS) && (currentstep < MICROSTEPS*2)):
                latch_state |= b | c
            if ((currentstep >= MICROSTEPS*2) && (currentstep < MICROSTEPS*3)):
                latch_state |= c | d
            if ((currentstep >= MICROSTEPS*3) && (currentstep < MICROSTEPS*4)):
                latch_state |= d | a
        else:
            if (currentstep/(MICROSTEPS/2)==0):
                latch_state |= a; # energize coil 1 only
            elif (currentstep/(MICROSTEPS/2)==1):
                latch_state |= a | b; # energize coil 1+2
            elif (currentstep/(MICROSTEPS/2)==2):
                latch_state |= b; # energize coil 2 only
            elif (currentstep/(MICROSTEPS/2)==3):
                latch_state |= b | c; # energize coil 2+3
            elif (currentstep/(MICROSTEPS/2)==4):
                latch_state |= c; # energize coil 3 only
            elif (currentstep/(MICROSTEPS/2)==5):
                latch_state |= c | d; # energize coil 3+4
            elif (currentstep/(MICROSTEPS/2)==6):
                latch_state |= d; # energize coil 4 only
            elif (currentstep/(MICROSTEPS/2)==7):
                latch_state |= d | a; # energize coil 1+4

        self.latch_tx()
        return currentstep


    def release(self):
        if (self.steppernum == 1):
            # all motor pins to 0
            latch_state &= ~BV(M1['A']) & ~BV(M1['B']) & ~BV(M2['A']) & ~BV(M2['B'])
        elif (steppernum == 2) :
            # all motor pins to 0
            latch_state &= ~BV(M3['A']) & ~BV(M3['B']) & ~BV(M4['A']) & ~BV(M4['B'])
        self.latch_tx()

def main():
    mot1 = AF_DCMotor(1, 100)
    mot2 = AF_DCMotor(1, 100)
    #mot1.run(FORWARD)
    #sleep(5)
    mot1.run(RELEASE)
    mot1.run(RELEASE)
    gpio.cleanup()

if __name__=="__main__":
    main()
