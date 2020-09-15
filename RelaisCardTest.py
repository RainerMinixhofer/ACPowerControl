#!/usr/bin/python3
# -*- coding:utf-8 -*-
#pylint: disable=C0103,E0401
"""
Demo how to access Relais cards through MCP23017 port expander
"""
import time
from MCP23017 import MCP23017

#create chip driver with bank=0 mode on address 0x20
mcp23017 = MCP23017(i2cbus=1, device=0x20, bank=0, resetpin=4)
#Set all Pins of GPA and GPB of MCP23017 to output
mcp23017.setregister("iodira", value=0x00)
mcp23017.setregister("iodirb", value=0x00)
#Check if the registers have been properly set
try:
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
    del mcp23017
