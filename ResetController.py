#!/usr/bin/python3
# -*- coding:utf-8 -*-
#pylint: disable=C0103,E0401
"""
Resets MCP23017 Controller by pulling reset line low for 10 us
"""
import time
import RPi.GPIO as GPIO #pylint: disable=E0401

GPIO.setmode(GPIO.BCM)
#Enable MCP23017 by setting reset pin (connected to BCM4) to high
RESET_PIN = 4
GPIO.setup(RESET_PIN, GPIO.OUT, initial=GPIO.HIGH)
GPIO.output(RESET_PIN, GPIO.LOW)
time.sleep(0.0001)
GPIO.output(RESET_PIN, GPIO.HIGH)
print("MCP23017 resetted")
