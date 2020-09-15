#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 13 11:57:51 2020

pytest file testing I2C bus

@author: Rainer Minixhofer
"""

import subprocess

def test_i2c_addr():
    """
    Test if both I2C devices on bus at 0x20 and 0x40 can be found
    """
    completedprocess = subprocess.run(["i2cdetect", "-y", "1"], \
                                      capture_output=True, text=True, check=False)
    assert completedprocess.stderr==''
    output = completedprocess.stdout.split("\n")[1:]
    output = [line.split()[1:] for line in output]
    output = [item for sublist in output for item in sublist]
    i2caddrlist = [int('0x'+item,0) for item in output if item != '--']
    assert i2caddrlist == [32, 64]

def test_i2c_functionalities():
    """
    Test if functionalities given by i2cdetect -F of bus 1 match expectations
    """
    completedprocess = subprocess.run(["i2cdetect", "-F", "1"], \
                                      capture_output=True, text=True, check=False)
    assert completedprocess.stderr==''
    output = completedprocess.stdout.split("\n")[1:-1]
    output = [line.split()[-1] for line in output]
    assert output == ['yes'] * 10 + ['no'] * 2 + ['yes'] * 3

def test_i2c_speed():
    """
    Checks if I2C bus speed is set to 400 kByte/s = 3.2 MBit/s = high speed I2C mode
    """
    file = open('/sys/class/i2c-adapter/i2c-1/of_node/clock-frequency', 'rb')
    value = file.read()
    assert int.from_bytes(value, byteorder='big') == 400000

#test_i2cdetect_addr()
#test_i2cdetect_functionalities()
#test_i2c_speed()
