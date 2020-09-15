#!/usr/bin/python3
# -*- coding:utf-8 -*-
#pylint: disable=C0103,E0401
"""
Test Critical 220V Supply Switching to measure Supply Disturbance
"""
import RPi.GPIO as GPIO
from MCP23017 import MCP23017

GPIO.setmode(GPIO.BCM)
#Enable MCP23017 by setting reset pin (connected to BCM4) to high
RESET_PIN = 4
GPIO.setup(RESET_PIN, GPIO.OUT)
GPIO.output(RESET_PIN, GPIO.HIGH)

#create chip driver with bank=0 mode on address 0x20
mcp23017 = MCP23017(i2cbus=1, device=0x20, bank=0)
#Set all Pins of GPA and GPB of MCP23017 to output
mcp23017.setregister("iodira", value=0x00)
mcp23017.setregister("iodirb", value=0x00)
#Check if the registers have been properly set
try:
    print("Direction register of port A: 0x{:02X}".format(mcp23017.getregister("iodira")))
    print("Direction register of port B: 0x{:02X}".format(mcp23017.getregister("iodirb")))
    print("Switching 220V supply on...")
    mcp23017.enable("Mains")
    input("Press key to switch 220V supply off...")
    mcp23017.disable("Mains")
    print("End Test")

finally:
    GPIO.cleanup()
