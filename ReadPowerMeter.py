#!/usr/bin/python3
# -*- coding: utf-8 -*-
#pylint: disable=C0103,C0301
"""
Test Read/Write to INA260 via I2C

Created on Sat Aug 29 22:12:34 2020

@author: Rainer Minixhofer
"""

import time
import os
from math import sqrt, log10, floor
from statistics import mean, stdev
import numpy as np
import INA260 #pylint: disable=E0401
from MCP23017 import MCP23017

#create chip driver with bank=0 mode on address 0x20
#reset it to initialize via GPIO pin 4 of Raspi
mcp23017 = MCP23017(i2cbus=1, device=0x20, bank=0, resetpin=4)
#configure all pins of both ports as outputs (bitwise) with state off
mcp23017.all_to_output()
#Set all relais to provide 12.0V (without switching on mains yet)
mcp23017.setregister("gpioa", value=0x20)
mcp23017.setregister("gpiob", value=0x80)

#Initialize I2C Bus #1 for INA260 with address 0x40
#Set Averaging mode for 512 averages at 1.1ms conversion time
#in continous mode measuring Shunt Current and Bus Voltage
ina260 = INA260.INA260Controller(alertpin=13, avg=512, vbusct=1100, ishct=1100, meascont=True, \
                                 measi=True, measv=True, Rdiv1=220)
print("Manufacturer ID: 0x{:02X} (should be 0x5449)".format(ina260.manufacturer_id))
print("Die ID: 0x{:02X} (should be 0x227)".format(ina260.die_id))
print("Die Revision: 0x{:01X} (should be 0x0)".format(ina260.die_rev))
#Configure ALERT pin to be asserted when the conversion ready flag, the bus voltage over limit \
#and the under current limit is asserted.")
ina260.alert = ['Bus Voltage Over Voltage']
print("Showing Bus Voltage and Alert Flag with 500ms update interval. Press CTRL-C to move to next output....")

mcp23017.enable("Mains")

while True:

    try:
        print("Bus voltage: {:+03.5f} V / Alert Flag {}".\
              format(ina260.voltage() * sqrt(2), ina260.alertflag), end='\r')
        time.sleep(0.5)
    except KeyboardInterrupt:
        break

filename = "samples.txt"
if os.path.exists(filename):
    os.remove(filename)

#Use fastest setting to measure voltage (no averaging, shortest conversion time and no current
#measurement)

ina260.avg = 1
ina260.measi = False
ina260.vbusct = 140
ina260.alert = ['Conversion Ready']

count = n = 300
samples = []

#Sample <count> measurements
while count > 0:
    ina260.wait_for_alert_edge(timeout='Automatic')
    samples.append(ina260.voltage())

    count -= 1

effective = []
startindex = 0
for i in range(len(samples)-1):
    pair = samples[i:i+2]
    if pair[0] < 0.1 < pair[1]:
        #Calculate average of period between startindex from
        #previous period and identified new startindex
        average = np.trapz(samples[startindex:i]) / (i-startindex+1)
        effective.append(average * sqrt(2))
        startindex = i
        print("Effective value: {:5.3f}V".format(effective[-1]))

#Calculate mean value over all measured periods but drop the
#incomplete first and last period
def round_to_1(x, ref=None):
    """
    rounds x to most significant digit
    if ref is specified x ist rounded to the most significant digit of ref
    """
    if ref is None:
        ref = x
    return round(x, -int(floor(log10(abs(ref)))))

error = sqrt((stdev(effective[1:-1]) ** 2)/n)
print("Mean effective value {}\u00B1{}V".format(round_to_1(mean(effective[1:-1]), ref=error), round_to_1(error)))

logfile = open(filename, 'w')
logfile.writelines(map(lambda x: str(x)+'\n', samples))
logfile.close()

assert os.path.exists(filename)

mcp23017.disable("Mains")
mcp23017.setregister("gpioa", value=0x00)
mcp23017.setregister("gpiob", value=0x00)

print("Measurement done")

del mcp23017
