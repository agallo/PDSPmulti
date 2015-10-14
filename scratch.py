!#/usr/bin/python

__author__ = 'agallo'


import wiringpi2 as wiringpi

wiringpi.wiringPiSetupPhys()


LOW = 0
HIGH = 1
OUTPUT = 1

DSP0 = 22   # CE for display 0
DSP1 = 24   # CE for display 1


wiringpi.pinMode(DSP0, OUTPUT)
wiringpi.pinMode(DSP1, OUTPUT)

wiringpi.digitalWrite(DSP0, HIGH)
wiringpi.digitalWrite(DSP1, HIGH)

wiringpi.digitalWrite(DSP0, LOW)
wiringpi.digitalWrite(DSP1, LOW)