#!/usr/bin/python3
"""
KY40EncoderTest.py tests basic functionality of reading the KY-40
Encoder with the RasPi
"""
# pylint: disable=C0103,W0603
# coding=utf-8
# Needed modules will be imported and configured
import time
import RPi.GPIO as GPIO #pylint: disable=E0401

GPIO.setmode(GPIO.BCM)

# Declaration and initialisation of the input pins which are connected with the sensor.
PIN_CLK = 21
PIN_DT = 20
BUTTON_PIN = 16
# List to decode 4-bit transition state of encoder into invalid(0), CW(1) and CCW(-1) transition
ENCODERSTATES = [0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0]

GPIO.setup(PIN_CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Needed variables will be initialised
Counter = 0
CWDir = True
# Initial reading of CLK and DT pins
EncState = GPIO.input(PIN_CLK) << 1 + GPIO.input(PIN_DT)
delayTime = 0.01

def ReadEncoder(_):
    """
    This output function will start at signal detection
    It uses 4-bit transition state to detect if the current state together
    with the previous state resemble a valid (CW or CCW) movement or an
    invalid (bouncing induced) one.
    ENCODERSTATES describe the respective truth table where the index is
    the transition state value and the entries are the respective validity
    infos (0 being invalid -1 being CCW and 1 being CW)
    see code snippets from
    https://hifiduino.wordpress.com/2010/10/20/rotaryencoder-hw-sw-no-debounce/
    and https://hifiduino.wordpress.com/2010/10/20/rotaryencoder-hw-sw-no-debounce/
    """
    global Counter
    global EncState
    global CWDir

    #remember previous state
    EncState <<= 2
    #Read current CLK and DT pin reading after edge detection and add state
    EncState |= (GPIO.input(PIN_CLK) << 1 + GPIO.input(PIN_DT)) & 0x03

    result = ENCODERSTATES[ EncState & 0x0F ]
    if result != 0:

        Counter += result
        CWDir = result > 0

        print("Rotation detected: ")

        if CWDir:
            print("Rotational direction: Clockwise")
        else:
            print("Rotational direction: Counterclockwise")
        print("Current position: ", Counter)
        print("------------------------------")

def CounterReset(channel): #pylint: disable=W0613
    """
    Reset the Counter
    """
    global Counter

    print("Position reset!")
    print("------------------------------")
    Counter = 0

# To include a debounce, the output function will be initialised from the
# GPIO Python Module
# Typical bouncetimes are below 10ms (see debouncing.pdf document)
# The remaining longer bouncing need to be collected by the software debounce
# method using 4-bit transition values
GPIO.add_event_detect(PIN_CLK, GPIO.BOTH, callback=ReadEncoder, \
    bouncetime=10)
GPIO.add_event_detect(PIN_DT, GPIO.BOTH, callback=ReadEncoder, \
    bouncetime=10)
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=CounterReset, \
    bouncetime=10)

print("Sensor-Test [press ctrl-c to end]")

# Main program loop
try:
    while True:
        time.sleep(delayTime)

# Scavenging work after the end of the program

except KeyboardInterrupt:
    GPIO.cleanup()
