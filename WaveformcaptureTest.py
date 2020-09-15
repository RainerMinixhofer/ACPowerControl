#!/usr/bin/python3
# -*- coding: utf-8 -*-
#pylint: disable=C0103,C0301
"""
Measure AC Waveform using INA260

@author: Rainer Minixhofer
"""

import time
import csv
from datetime import datetime
import RPi.GPIO as GPIO #pylint: disable=E0401
import INA260 #pylint: disable=E0401
from MCP23017 import MCP23017

GPIO.setmode(GPIO.BCM)
#Enable MCP23017 by setting reset pin (connected to BCM4) to high
RESET_PIN = 4
GPIO.setup(RESET_PIN, GPIO.OUT)
GPIO.output(RESET_PIN, GPIO.HIGH)

#create chip driver with bank=0 mode on address 0x20
mcp23017 = MCP23017(i2cbus=1, device=0x20, bank=0)
#configure all pins of both ports as outputs (bitwise)
for bit in range(8):
    mcp23017.disable(port="a", bit=bit)
    mcp23017.disable(port="b", bit=bit)
#Set all relais to provide 12.0V (without switching on mains yet)
mcp23017.setregister("gpioa", value=0x20)
mcp23017.setregister("gpiob", value=0x80)

mcp23017.enable("Mains")

#INA260 Power Meter has address 0x20 on I2C Bus #1
#Set Averaging mode for no averages at 1.1ms conversion time in continous mode
#measuring Shunt Current and Bus Voltage. Voltage divider resistor is 220kOhm

sampleperiod = 140 # in Microseconds

ina260 = INA260.INA260Controller(avg=1, vbusct=sampleperiod, ishct=sampleperiod, meascont=True, \
                                 measi=True, measv=True, Rdiv1=220)
#Reset INA260
ina260.reset()

#Read configuration register 0x00 from INA260
print("Manufacturer ID: 0x{:02X} (should be 0x5449)".format(ina260.manufacturer_id()))
print("Die ID: 0x{:02X} (should be 0x227)".format(ina260.die_id()))
print("Die Revision: 0x{:01X} (should be 0x0)".format(ina260.die_rev()))

while True:

    try:
        print("Bus current: {:+03.5f} A / Bus voltage: {:+03.5f} V / Bus power: {:03.5f} W / Alert Flag {}".\
              format(ina260.current(), ina260.voltage(), ina260.power(), ina260.alertflag), end='\r')
        time.sleep(0.5)
    except KeyboardInterrupt:
        break

print("Collecting AC Waveform with 1.1msec sampling interval.")

nrsamples = 500

bus_voltage = [0]
dt = [0]
try:
    starttime = datetime.now()
    while len(bus_voltage) < nrsamples:
        bus_voltage.append(ina260.voltage())
        dt.append((datetime.now() - starttime).microseconds)
        time_to_sleep = (sampleperiod - dt[-1] + dt[-2]) / 1000000
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)

except KeyboardInterrupt:
    exit()

finally:
    GPIO.cleanup()

mcp23017.disable("Mains")

with open('/home/rainer/Documents/ACPowerControl/VAC_profile.txt', 'w') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerows(zip(dt, bus_voltage))
    f.close()

print("\nEnd of Test")
