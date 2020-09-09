#!/usr/bin/python3
# -*- coding:utf-8 -*-
#pylint: disable=C0103,E0401
"""
Demo how to access Relais cards through MCP23017 port expander
"""
import time
import RPi.GPIO as GPIO
import smbus
from MCP23017 import MCP23017

GPIO.setmode(GPIO.BCM)
#Enable MCP23017 by setting reset pin (connected to BCM4) to high
RESET_PIN = 4
GPIO.setup(RESET_PIN, GPIO.OUT)
GPIO.output(RESET_PIN, GPIO.HIGH)

#create chip with bank=1 mode on address 0x20
mcp23017 = MCP23017()
#configure all pins of both ports as outputs
for pin in mcp23017.pins.values():
    pin.disable()

print("Direction of Mains pin:",mcp23017.pins["Mains"].dirreg)
#mypin=pin(mcp23017,"gpiob",0)
#mypin.enable()
#time.sleep(1)
#mypin.disable()

exit()

#Initialize I2C Bus #1 for MCP23017 with address 0x20
address = 0x20
bus = smbus.SMBus(1)
#Set all Pins of GPA and GPB of MCP23017 to output
bus.write_byte_data(address, 0x00, 0x00)
bus.write_byte_data(address, 0x01, 0x00)
#Check if the registers have been properly set
try:
    print("Register setting at 0x00:", bus.read_byte_data(address, 0x00))
    print("Register setting at 0x01:", bus.read_byte_data(address, 0x01))
    print("Switching Relais in sequence every second...")
    print("First Port GPA")
    bus.write_byte_data(address, 0x14, 0x01)
    time.sleep(1.0)
    bus.write_byte_data(address, 0x14, 0x02)
    time.sleep(1.0)
    bus.write_byte_data(address, 0x14, 0x04)
    time.sleep(1.0)
    bus.write_byte_data(address, 0x14, 0x08)
    time.sleep(1.0)
    bus.write_byte_data(address, 0x14, 0x10)
    time.sleep(1.0)
    bus.write_byte_data(address, 0x14, 0x20)
    time.sleep(1.0)
    bus.write_byte_data(address, 0x14, 0x40)
    time.sleep(1.0)
    bus.write_byte_data(address, 0x14, 0x80)
    time.sleep(1.0)
    bus.write_byte_data(address, 0x14, 0x00)
    print("Then Port GPB")
    bus.write_byte_data(address, 0x15, 0x01)
    time.sleep(1.0)
    bus.write_byte_data(address, 0x15, 0x02)
    time.sleep(1.0)
    bus.write_byte_data(address, 0x15, 0x04)
    time.sleep(1.0)
    bus.write_byte_data(address, 0x15, 0x08)
    time.sleep(1.0)
    bus.write_byte_data(address, 0x15, 0x10)
    time.sleep(1.0)
    bus.write_byte_data(address, 0x15, 0x20)
    time.sleep(1.0)
    bus.write_byte_data(address, 0x15, 0x40)
    time.sleep(1.0)
    bus.write_byte_data(address, 0x15, 0x80)
    time.sleep(1.0)
    bus.write_byte_data(address, 0x15, 0x00)
    print("End Test")

finally:
    GPIO.cleanup()
