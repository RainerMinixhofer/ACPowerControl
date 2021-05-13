#!/usr/bin/python3
# pylint: disable=C0103
# coding=utf-8
# Needed modules will be imported and configured
"""
Test routine for LED Switch
Switches LED on when Switch is on and off when off
"""
import time
import pytest
import RPi.GPIO as GPIO #pylint: disable=E0401

@pytest.mark.interactive
def test_LEDDruckschalter():
    """
    Test routine for LED Switch
    Switches LED on when Switch is on and off when off
    """
    delayTime = 0.01
    countdown = 5
    GPIO.setmode(GPIO.BCM)

    # Declaration and initialisation of the input pins which are connected with the sensor.
    BUTTON_PIN = 26
    LED_PIN = 19

    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(LED_PIN, GPIO.OUT)

    def FlankDetect(channel):
        """
        Runs when change of BUTTON-PIN State has been detected
        """
        nonlocal countdown
        time.sleep(0.2) # Wait till bouncing ends
        channel_state = not GPIO.input(channel) #Button pin input is inverted
        if channel_state:
            countdown = countdown - 1
            print("LED is on and switch closed (%d cycles remaining)" % countdown)
        else:
            print("LED is off and switch open (%d cycles remaining)" % countdown)
        GPIO.output(LED_PIN, channel_state)

    # Initialize LED with right state of button
    state = not GPIO.input(BUTTON_PIN)
    GPIO.output(LED_PIN, state)

    # To include a debounce, the output function will be initialised from the
    # GPIO Python Module
    GPIO.add_event_detect(BUTTON_PIN, GPIO.BOTH, callback=FlankDetect, \
        bouncetime=300)

    print("Testing of signal light when LED Switch is on")
    print("LED-Test (%d cycles remaining)" % countdown)

    # Main program loop
    try:
        while countdown>0:
            time.sleep(delayTime)
        GPIO.cleanup()
    # Scavenging work after the end of the program

    except KeyboardInterrupt:
        GPIO.cleanup()
        