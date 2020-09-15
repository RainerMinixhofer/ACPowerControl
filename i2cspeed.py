#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 13 11:57:51 2020

returns I2C bus speed setting

@author: Rainer Minixhofer
Checks if I2C bus speed is set to 400 kByte/s = 3.2 MBit/s = high speed I2C mode
"""

f = open('/sys/class/i2c-adapter/i2c-1/of_node/clock-frequency', 'rb')
value = f.read()
speedbyte = int.from_bytes(value, byteorder='big')
speedbit = speedbyte * 8

if speedbit > 1000000:
    MODE = 'high speed mode'
elif speedbit > 400000:
    MODE = 'fast mode'
elif speedbit > 100000:
    MODE = 'full speed mode'
else:
    MODE = 'normal mode'
print('I2C Bus Speed: {} kByte/s = {} kBit/s ({})'.format(speedbyte, speedbit, MODE))
