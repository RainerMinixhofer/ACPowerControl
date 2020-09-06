#!/usr/bin/python3
# -*- coding: utf-8 -*-
#pylint: disable=C0103,C0301
"""
Test Read/Write to INA260 via I2C

Created on Sat Aug 29 22:12:34 2020

@author: Rainer Minixhofer
"""

import time
import INA260 #pylint: disable=E0401

def bend2lend(value):
    """
    Converts integer value <value> from big endian to little endian and vice versa
    """
    result = ((value&(255<<8))>>8)|((value&255)<<8)
    if result > 32767:
        result -= 1
        result = -((~result) & 65535)
    return result

#Initialize I2C Bus #1 for INA260 with address 0x40
#Set Averaging mode for 512 averages at 1.1ms conversion time
#in continous mode measuring Shunt Current and Bus Voltage
ina260 = INA260.INA260Controller(avg=1,vbusct=140,ishct=140,meascont=True,measi=True,measv=True)
print("Manufacturer ID: 0x{:02X} (should be 0x5449)".format(ina260.manufacturer_id()))
print("Die ID: 0x{:02X} (should be 0x227)".format(ina260.die_id()))
print("Die Revision: 0x{:01X} (should be 0x0)".format(ina260.die_rev()))
#Read configuration register 0x00 from INA260
print("Configuration Register Content: 0x{:0X} (should be 0x6007".format(ina260.configreg))
ina260.reset()
print("Configuration Register Content: 0x{:0X} (should be 0x6127)".format(ina260.configreg))
#Set Averaging mode for 512 averages at 204us conversion time in trigger mode measuring only Bus Voltage
ina260.avg = 512
ina260.vbusct = 204
ina260.ishct = 204
ina260.meascont = False
ina260.measi = False
ina260.measv = True
print("Configuration Register Content: 0x{:0X} (should be 0x6C4A)".format(ina260.configreg))
#Set Averaging mode for 1 averages at 140us conversion time in continous mode measuring Bus Voltage and Shunt Current
ina260.reset()
ina260.avg = 1
ina260.vbusct = 140
ina260.ishct = 140
print("Configuration Register Content: 0x{:0X} (should be 0x6007)".format(ina260.configreg))
print("Configure ALERT pin to be asserted when the conversion ready flag, the bus voltage over limit \
and the under current limit is asserted.")
ina260.alert = ['Conversion Ready', 'Power Over Limit', 'Bus Voltage Under Voltage', 'Over Current Limit']
print("Mask/Enable Register Content: 0x{:04X} (should be 0x1408)".format(ina260.mask_enablereg))
ina260.alertlimit = 0.002
print("Alert Limit Register Content: {:7.5f} V (0.002 V corrected to integer factor of LSB unit)".format(ina260.alertlimit))
print("Showing Current, Bus Voltage and Power registers with 500ms update interval. Press CTRL-C to move to next output....")

while True:

    try:
        print("Bus current: {:+03.5f} A / Bus voltage: {:+03.5f} V / Bus power: {:03.5f} W / Alert Flag {}".\
              format(ina260.current(), ina260.voltage(), ina260.power(), ina260.alertflag), end='\r')
        time.sleep(0.5)
    except KeyboardInterrupt:
        break

print("\nEnd of Test")
