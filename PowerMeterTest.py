#!/usr/bin/python3
# -*- coding: utf-8 -*-
#pylint: disable=C0103,C0301
"""
Test Read/Write to INA260 via I2C

Created on Sat Aug 29 22:12:34 2020

@author: Rainer Minixhofer
"""

import time
from math import sqrt
import INA260 #pylint: disable=E0401
from MCP23017 import MCP23017

#create chip driver with bank=0 mode on address 0x20
#reset it to initialize via GPIO pin 4 of Raspi
mcp23017 = MCP23017(i2cbus=1, device=0x20, bank=0, resetpin=4)
#configure all pins of both ports as outputs (bitwise)
for bit in range(8):
    mcp23017.disable(port="a", bit=bit)
    mcp23017.disable(port="b", bit=bit)
#Set all relais to provide 12.0V (without switching on mains yet)
mcp23017.setregister("gpioa", value=0x20)
mcp23017.setregister("gpiob", value=0x80)

#Initialize I2C Bus #1 for INA260 with address 0x40
#Set Averaging mode for 512 averages at 1.1ms conversion time
#in continous mode measuring Shunt Current and Bus Voltage
ina260 = INA260.INA260Controller(avg=512, vbusct=1100, ishct=1100, meascont=True, \
                                 measi=True, measv=True, Rdiv1=220)
print("Manufacturer ID: 0x{:02X} (should be 0x5449)".format(ina260.manufacturer_id))
print("Die ID: 0x{:02X} (should be 0x227)".format(ina260.die_id))
print("Die Revision: 0x{:01X} (should be 0x0)".format(ina260.die_rev))
#Configure ALERT pin to be asserted when the conversion ready flag, the bus voltage over limit \
#and the under current limit is asserted.")
ina260.alert = ['Conversion Ready', 'Power Over Limit', 'Bus Voltage Under Voltage', 'Over Current Limit']
print("Showing Bus Voltage and Alert Flag with 500ms update interval. Press CTRL-C to move to next output....")

mcp23017.enable("Mains")


while True:

    try:
        print("Bus voltage: {:+03.5f} V / Alert Flag {}".\
              format(ina260.voltage() * sqrt(2), ina260.alertflag), end='\r')
        time.sleep(0.5)
    except KeyboardInterrupt:
        break

#Capture data with highest possible rate over 1000 samples
#Set Averaging mode for 1 averages at 140us conversion time in continous mode measuring Bus Voltage and Shunt Current
ina260.reset()
ina260.avg = 1
ina260.vbusct = 140
ina260.ishct = 140

count = 500
samples = [
    ]
#Screen successive equal measurements
while count > 0:
    if len(samples) == 0 or ina260.voltage() != samples[-1]:
        samples.append(ina260.voltage())
    count -= 1

logfile = open('samples.txt', 'w')
logfile.writelines(map(lambda x: str(x)+'\n', samples))
logfile.close()

try:
    mcp23017.disable("Mains")
    mcp23017.setregister("gpioa", value=0x00)
    mcp23017.setregister("gpiob", value=0x00)

    print("\nEnd of Test")

finally:
    del mcp23017
