# pylint: disable=C0103
# coding=utf-8
# Needed modules will be imported and configured
"""
Test routine for LED Switch
Switches LED on when Switch is on and off when off
"""
import time
import RPi.GPIO as GPIO

delayTime = 0.01
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
    time.sleep(0.2) # Wait till bouncing ends
    channel_state = not GPIO.input(channel) #Button pin input is inverted
    GPIO.output(LED_PIN, channel_state)

# Initialize LED with right state of button
state = not GPIO.input(BUTTON_PIN)
GPIO.output(LED_PIN, state)

# To include a debounce, the output function will be initialised from the
# GPIO Python Module
GPIO.add_event_detect(BUTTON_PIN, GPIO.BOTH, callback=FlankDetect, \
    bouncetime=300)

print("LED-Test [press ctrl-c to end]")

# Main program loop
try:
    while True:
        time.sleep(delayTime)

# Scavenging work after the end of the program

except KeyboardInterrupt:
    GPIO.cleanup()
