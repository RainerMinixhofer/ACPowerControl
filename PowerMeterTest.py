#!/usr/bin/python3
# -*- coding: utf-8 -*-
#pylint: disable=C0103,C0301
"""
Test Read/Write to INA260 via I2C

Created on Sat Aug 29 22:12:34 2020

@author: Rainer Minixhofer
"""

import time
import smbus #pylint: disable=E0401

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
address = 0x40
bus = smbus.SMBus(1)
#Read configuration register 0x00 from INA260
print("Configuration Register:", hex(bend2lend(bus.read_word_data(address, 0x00))), "should be 0x6127")
print("Manufacturer ID Register:", hex(bend2lend(bus.read_word_data(address, 0xFE))), "should be 0x5449")
print("Die ID Register:", hex(bend2lend(bus.read_word_data(address, 0xFF))), "should be 0x2270")

print("Showing Current, Bus Voltage and Power registers with 500ms update interval. Press CTRL-C to move to next output....")

while True:

    try:
        val = bus.read_word_data(address, 0x01)
        print("Current Register: {:7.2f}mA ({:>6})".format(bend2lend(val) * 1.25, hex(val)), end="\r")
        time.sleep(0.5)
    except KeyboardInterrupt:
        break

print("\n")

while True:

    try:
        val = bus.read_word_data(address, 0x02)
        print("Bus Voltage Register: {:7.2f}mV ({:>6})".format(bend2lend(val) * 1.25, hex(val)), end="\r")
        time.sleep(0.5)
    except KeyboardInterrupt:
        break

print("\n")

while True:

    try:
        val = bus.read_word_data(address, 0x03)
        print("Power Register: {:5d}mW ({:>6})".format(bend2lend(val) * 10, hex(val)), end="\r")
        time.sleep(0.5)
    except KeyboardInterrupt:
        break

print("\nEnd of Test")
