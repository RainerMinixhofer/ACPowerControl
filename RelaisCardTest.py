#!/usr/bin/python3
# -*- coding:utf-8 -*-
#pylint: disable=C0103,E0401
"""
Demo how to access Relais cards through MCP23017 port expander
"""
import time
import RPi.GPIO as GPIO
from MCP23017 import MCP23017

GPIO.setmode(GPIO.BCM)
#Enable MCP23017 by setting reset pin (connected to BCM4) to high
RESET_PIN = 4
GPIO.setup(RESET_PIN, GPIO.OUT)
GPIO.output(RESET_PIN, GPIO.HIGH)

#create chip driver with bank=0 mode on address 0x20
mcp23017 = MCP23017(i2cbus=1, device=0x20, bank=0)
#Test several register access methods
print("Direction register of port A: 0x{:02X}".format(mcp23017.getregister("iodira")))
print("Direction register of port B: 0x{:02X}".format(mcp23017.getregister("iodirb")))
print("Direction of Mains pin:",mcp23017.getregister(register="iodir", pin="Mains"))

mcp23017.disable(pin="Mains")

print("Direction of Mains pin:",mcp23017.getregister(register="iodir", pin="Mains"))


print("Direction register of port A: 0x{:02X}".format(mcp23017.getregister("iodira")))
print("Direction register of port B: 0x{:02X}".format(mcp23017.getregister("iodirb")))

#configure all pins of both ports as outputs (bitwise)
for bit in range(8):
    mcp23017.disable(port="a",bit=bit)
    mcp23017.disable(port="b",bit=bit)

print("Direction register of port A: 0x{:02X}".format(mcp23017.getregister("iodira")))
print("Direction register of port B: 0x{:02X}".format(mcp23017.getregister("iodirb")))

#Other method to set all Pins of GPA and GPB of MCP23017 to output
mcp23017.setregister(mcp23017.getregister("iodira"), value=0x00)
mcp23017.setregister(mcp23017.getregister("iodirb"), value=0x00)
#Check if the registers have been properly set
try:
    print("Direction register of port A: 0x{:02X}".format(mcp23017.getregister("iodira")))
    print("Direction register of port B: 0x{:02X}".format(mcp23017.getregister("iodirb")))
    print("Switching Relais in sequence every second...")
    print("First Port GPA")
    for bit in range(8):
        mcp23017.enable(port="a",bit=bit)
        time.sleep(1.0)
        mcp23017.disable(port="a",bit=bit)
    print("Then Port GPB")
    for bit in range(8):
        mcp23017.enable(port="b",bit=bit)
        time.sleep(1.0)
        mcp23017.disable(port="b",bit=bit)
    print("End Test")

finally:
    GPIO.cleanup()
