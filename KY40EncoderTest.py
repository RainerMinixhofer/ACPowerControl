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
# TODO: Implement Code from https://www.best-microcontroller-projects.com/rotary-encoder.html
PIN_CLK = 21
PIN_DT = 20
BUTTON_PIN = 16

GPIO.setup(PIN_CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Needed variables will be initialised
Counter = 0
Richtung = True
PIN_CLK_LETZTER = 0
PIN_CLK_AKTUELL = 0
delayTime = 0.01

# Initial reading of Pin_CLK
PIN_CLK_LETZTER = GPIO.input(PIN_CLK)

def ausgabeFunktion(channel):
    """
    This output function will start at signal detection
    """
    global Counter
    global PIN_CLK_AKTUELL
    global Richtung

    PIN_CLK_AKTUELL = GPIO.input(channel)

    if PIN_CLK_AKTUELL != PIN_CLK_LETZTER:

        if GPIO.input(PIN_DT) != PIN_CLK_AKTUELL:
            Counter += 1
            Richtung = True
        else:
            Richtung = False
            Counter = Counter - 1

        print("Rotation detected: ")

        if Richtung:
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
GPIO.add_event_detect(PIN_CLK, GPIO.BOTH, callback=ausgabeFunktion, \
    bouncetime=300)
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=CounterReset, \
    bouncetime=300)

print("Sensor-Test [press ctrl-c to end]")

# Main program loop
try:
    while True:
        time.sleep(delayTime)

# Scavenging work after the end of the program

except KeyboardInterrupt:
    GPIO.cleanup()
