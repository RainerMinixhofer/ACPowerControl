#!/usr/bin/python3
# -*- coding: utf-8 -*-
#pylint: disable=C0103,C0301
"""
Test Read/Write to INA260 via I2C

Created on Sat Aug 29 22:12:34 2020

@author: Rainer Minixhofer
"""

import time
import os.path
from math import isclose, sqrt
import numpy as np
import pytest
import INA260 #pylint: disable=E0401
from MCP23017 import MCP23017

@pytest.fixture
def mcp23017():
    """
    create chip driver with bank=0 mode on address 0x20, reset it to initialize
    via GPIO pin 4 of Raspi
    """
    portexpander = MCP23017(i2cbus=1, device=0x20, bank=0, resetpin=4)
    #configure all pins of both ports as outputs (bitwise)
    for bit in range(8):
        portexpander.disable(port="a", bit=bit)
        portexpander.disable(port="b", bit=bit)
    yield portexpander
    del portexpander
@pytest.fixture
def ina260():
    """
    Initialize I2C Bus #1 for INA260 with address 0x40
    Set Averaging mode for 512 averages at 1.1ms conversion time
    in continous mode measuring Shunt Current and Bus Voltage
    """
    meter = INA260.INA260Controller(avg=1, vbusct=140, ishct=140, meascont=True, \
                                     measi=True, measv=True, Rdiv1=220)
    yield meter
    del meter

def test_ina260_registeraccess(ina260):
    """
    Test access to registers of INA260 chip and write access and associated changes
    """
    assert ina260.manufacturer_id == 0x5449
    assert ina260.die_id == 0x227
    assert ina260.die_rev == 0x00
    #Read configuration register 0x00 from INA260
    assert ina260.configreg == 0x6007
    ina260.reset()
    assert ina260.configreg == 0x6127
    #Set Averaging mode for 512 averages at 204us conversion time in trigger mode measuring only Bus Voltage
    ina260.avg = 512
    ina260.vbusct = 204
    ina260.ishct = 204
    ina260.meascont = False
    ina260.measi = False
    ina260.measv = True
    assert ina260.configreg == 0x6C4A
    #Set Averaging mode for 1 averages at 140us conversion time in continous mode measuring Bus Voltage and Shunt Current
    ina260.reset()
    ina260.avg = 1
    ina260.vbusct = 140
    ina260.ishct = 140
    assert ina260.configreg == 0x6007
    #Configure ALERT pin to be asserted when the conversion ready flag, the bus voltage over limit
    #and the under current limit is asserted.
    ina260.alert = ['Conversion Ready', 'Power Over Limit', 'Bus Voltage Under Voltage', 'Over Current Limit']
    assert ina260.mask_enablereg == 0x8408
    ina260.alertlimit = 0.002
    assert isclose(ina260.alertlimit, 0.002, abs_tol=0.00125) # absolute accuracy is 1.25mV/LSB thus we set this limit

def test_ina260_measurement(mcp23017, ina260):
    """
    Test measuring of AC voltage by switching on mains and connecting other relais
    to provide 12V effective AC voltage
    """
    #Set all relais to provide 12.0V (without switching on mains yet)
    mcp23017.setregister("gpioa", value=0x20)
    mcp23017.setregister("gpiob", value=0x80)
    #we take a long conversion time of 1.1ms together with the highest
    #number of averaging samples, which should yield sufficient accuracy
    #to get a good estimate for the AC effective voltage
    #Since we have a single rectifier in the sensing circuit
    #The AC effective voltage measured is sqrt(2) times lower than the
    #effective voltage
    ina260.avg = 1024
    ina260.vbusct = 1100
    ina260.measv = True
    ina260.measi = False
    #Enable mains
    mcp23017.enable("Mains")
    print("Waiting 1sec to stabilize readings after mains switched on")
    time.sleep(1.0)
    print("Measuring....")
    while not ina260.conversionready:
        time.sleep(0.1)
    effvoltage = ina260.voltage() * sqrt(2)
    assert abs(effvoltage - 12.0) < 0.8
    print("Measurement done")

def test_ina260_sampling(mcp23017, ina260):
    """
    Capture measurement data with highest possible rate for 200 samples
    """
    filename = "samples.txt"
    if os.path.exists(filename):
        os.remove(filename)
    #Set all relais to provide 12.0V (without switching on mains yet)
    mcp23017.setregister("gpioa", value=0x20)
    mcp23017.setregister("gpiob", value=0x80)

    mcp23017.enable("Mains")
    print("Waiting 1sec to stabilize readings after mains switched on")
    time.sleep(1.0)
    print("Measuring....")

    count = 600
    samples = []
    #Screen successive equal measurements, thus we get less net samples 
    #than specified (about half)
    while count > 0:
        if len(samples) == 0 or ina260.voltage() != samples[-1]:
            samples.append(ina260.voltage())
        count -= 1

    skip1stperiod = True
    for i in range(len(samples)-1):
        pair = samples[i:i+2]
        if pair[0]<0.1 and pair[1]>0.1:
            if skip1stperiod:
                #First period (usually not complete). Save end index
                #for next period
                startindex = i+1
                skip1stperiod = False
            else:
                #Calculate average of period between startindex from
                #previous period and identified new startindex
                average = np.trapz(samples[startindex:i]) / (i-startindex+1)
                effective = average
                startindex = i
                print("Effective value:", effective)

    logfile = open(filename, 'w')
    logfile.writelines(map(lambda x: str(x)+'\n', samples))
    logfile.close()

    assert os.path.exists(filename)

    mcp23017.disable("Mains")
    mcp23017.setregister("gpioa", value=0x00)
    mcp23017.setregister("gpiob", value=0x00)

    print("Measurement done")
