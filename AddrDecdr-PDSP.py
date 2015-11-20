#!/usr/bin/python

from time import sleep
from time import strftime
import wiringpi2 as wiringpi


# TODO command line argument: -i (string to display (need to fiugre out how to accept special chars)
# TODO command line argument: -t (system local time, 12 hour (no AM or PM))
# TODO command line argument: -T (system local time, 24 hour)
# TODO command line argument: -u (UTC, 24 hour)
# TODO command line argument: -s (echo what is being sent to display to standard out)
# TODO gracefully handle SIG-INT (ctrl-c) and clear display upon exit


'''
hardware notes
using PDSP-1880 and 74LS595N (shift register) 74HC238 (address decoder)
see pin assignments for GPIO (header pin number) to variable to chip mapping
header pin column to be filled in after perfboard prototype is laid out
--- Power & Ground
Lead        destination                     header
GND         PDSP-16,18, ShfR-8,13           16
5V          PDSP-2,10,11,15,19 SfhR-10,16   15
additional (intra board, SR-->PDSP) connections documented here for completeness
ShfR -  PDSP
15      20
1       21
2       25
3       26
4       27
5       28
6       29
7       30
'''

# define pin names
# VAR = GPIO header     PDSP or Shift Register pin#     via header pin
RST = 3  # PDSP-1                        1
A0 = 5  # PDSP-3                        3
A1 = 7  # PDSP-4                        4
A2 = 11  # PDSP-5                        5
A3 = 13  # PDSP-6                        6
# CE = 15  # PDSP-14                       7 <--replaced by AddrDcdr Pins
WR = 19  # PDSP-13                       8
latch = 21  # ShiftRegister-12              10
SER = 23  # ShiftRegister-14              11
CLK = 18  # ShiftRegister-11              12
AD0 = 22  # Address Decoder Input A0
AD1 = 24  # Address Decoder Input A1
AD2 = 26  # Address Decoder Input A2
E3 = 12  # Address Decoder E2 (HIGH = all outputs LOW, ie enable = LOW)

pinlist = [RST, A0, A1, A2, A3, WR, latch, SER, CLK, AD0, AD1, AD2, E3]

# some wiringPi vars to make reading the code easier to read
LOW = 0
HIGH = 1
OUTPUT = 1


def setup():
    wiringpi.wiringPiSetupPhys()
    for pin in pinlist:
        wiringpi.pinMode(pin, OUTPUT)
    resetdisplay()


def resetdisplay():
    # some code to reset
    wiringpi.digitalWrite(RST, LOW)
    wiringpi.delayMicroseconds(1)
    wiringpi.digitalWrite(RST, HIGH)
    wiringpi.delayMicroseconds(150)
    wiringpi.digitalWrite(A3, HIGH)
    wiringpi.digitalWrite(AD0, LOW)
    wiringpi.digitalWrite(AD1, LOW)
    wiringpi.digitalWrite(AD2, LOW)
    wiringpi.digitalWrite(E3, HIGH)
    return


def scrolldisplay(istring, chip):
    for c in istring:
        tmpstr = ''.join(istring)
        print tmpstr[0:8]
        writedisplay(tmpstr, chip)
        istring.append(istring.pop(0))
        sleep(.3)
    return


def whichdisplay(display):
    '''
    select display to activate, using base 0 numbering
    PDSP with CE HIGH is the selected display
    display 255 is used to set all address decoder outputs
    (ie, all PDSP CE inputs) LOW
    '''
    print "entering whichdisplay, chip = " + str(display)
    if display == 255:
        print "XXX--->255, E3 going LOW"
        wiringpi.digitalWrite(E3, LOW)
        wiringpi.digitalWrite(AD0, LOW)
        wiringpi.digitalWrite(AD1, LOW)
        wiringpi.digitalWrite(AD2, LOW)
        return
    if display == 0:
        print "---->chip 0 selected, E3 HIGH, all others LOW"
        wiringpi.digitalWrite(E3, HIGH)
        wiringpi.digitalWrite(AD0, LOW)
        wiringpi.digitalWrite(AD1, LOW)
        wiringpi.digitalWrite(AD2, LOW)
        return
    if display == 1:
        print "-------->chip 1 selected, E3 HIGH, AD0 HIGH"
        wiringpi.digitalWrite(E3, HIGH)
        wiringpi.digitalWrite(AD0, HIGH)
        wiringpi.digitalWrite(AD1, LOW)
        wiringpi.digitalWrite(AD2, LOW)
        return


def writedisplay(whattodisplay):
    for pos in range(0, 8):
        if 1 & pos <> 0:
            wiringpi.digitalWrite(A0, HIGH)
        else:
            wiringpi.digitalWrite(A0, LOW)
        if 2 & pos <> 0:
            wiringpi.digitalWrite(A1, HIGH)
        else:
            wiringpi.digitalWrite(A1, LOW)
        if 4 & pos <> 0:
            wiringpi.digitalWrite(A2, HIGH)
        else:
            wiringpi.digitalWrite(A2, LOW)
        wiringpi.digitalWrite(latch, LOW)
        wiringpi.shiftOut(SER, CLK, 1, ord(whattodisplay[pos]))
        wiringpi.digitalWrite(latch, HIGH)
        wiringpi.delay(1)
        wiringpi.digitalWrite(E3, LOW)
        wiringpi.delay(1)
        wiringpi.digitalWrite(WR, LOW)
        wiringpi.delay(1)
        wiringpi.digitalWrite(WR, HIGH)
        wiringpi.delay(1)
        wiringpi.digitalWrite(E3, HIGH)
        wiringpi.delay(1)
    return


def pad(needtopad):
    while len(needtopad) <= 6:
        needtopad.append(' ')
        needtopad.insert(0, ' ')
    if len(needtopad) == 7:
        needtopad.append(' ')
    return needtopad


# main (to be replaced with arguments)
inputstring = '   EDT  '


# 24 hour time for input
# inputstring = time.strftime('%H:%M:%S')
# 24 hour time for input
# inputstring = time.strftime('%I:%M:%S')


def main():
    setup()
    while True:
        whichdisplay(0)
        writedisplay(list(strftime("%H:%M:%S")))
        sleep(1)
        whichdisplay(1)
        writedisplay(list(inputstring))
        sleep(1)


main()
