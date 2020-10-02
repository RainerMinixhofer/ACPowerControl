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
import json
from math import isclose, sqrt, floor, log10
from statistics import mean, stdev
import numpy as np #pylint: disable=E0401
import pytest
import INA260 #pylint: disable=E0401
from MCP23017 import MCP23017

@pytest.fixture(name='mcp23017')
def fixture_mcp23017():
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
@pytest.fixture(name="ina260")
def fixture_ina260():
    """
    Initialize I2C Bus #1 for INA260 with address 0x40
    Set Averaging mode for 512 averages at 1.1ms conversion time
    in continous mode measuring Shunt Current and Bus Voltage
    """
    meter = INA260.INA260Controller(alertpin=13, avg=1, vbusct=140, ishct=140, meascont=True, \
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
    assert isclose(ina260.alertlimit, 0.002, abs_tol=0.00125) # absolute accuracy is 1.25mV/LSB thus we set this as tolerance

def test_ina260_conversionreadyWithRegister(ina260):
    """
    Test conversion ready flag by using long conversion time and high amount of
    averaging
    """
    #Set INA260 to run long measurement with long conversion time (1.1ms) and highest
    #number of averages (1024) resulting in a measurement time of about 3 seconds
    ina260.reset()
    ina260.avg = 1024
    ina260.measv = True
    ina260.vbusct = 1100
    ina260.measi = False
    ina260.ishct = 1100
    expectedtime = ina260.avg * ina260.vbusct / 1000000
    #Trigger one measurement by setting MODE3 bit to zero
    ina260.meascont = False
    print("\nWaiting {:4.2f} seconds for conversion: ".format(expectedtime), end='')
    tstart = time.time()
    #Wait 2xtimes the expected measurment time to check if conversion ready flag shows up
    while not ina260.conversionready and (time.time() - tstart) < (2 * expectedtime):
        time.sleep(0.1)
    dt = time.time() - tstart
    assert dt < 2*expectedtime, print("Timeout of conversion ready detection")
    print("Conversion Ready detected after {:4.2f} secs".format(dt))
    #Test if only one measurement is done and no further (since trigger is set)
    #The reading of the conversionready property has cleared it already so
    #no new trigger within the test time period of 4 seconds should happening
    print("\nWaiting {:4.2f} seconds if conversion does not take place: ".format(expectedtime), end='')
    tstart = time.time()
    while not ina260.conversionready and (time.time() - tstart) < (2 * expectedtime):
        time.sleep(0.1)
    dt = time.time() - tstart
    assert dt >= 2 * expectedtime, print("Additional conversion ready flag detected")
    print("No conversion ready flag enable detected")
    #Try same test with double measurement time by switching on current measurement as well
    expectedtime = ina260.avg * (ina260.vbusct + ina260.vbusct) / 1000000
    ina260.measi = True # Writes into configuration register and thus triggers a new conversion
    print("\nWaiting {:4.2f} seconds for conversion: ".format(expectedtime), end='')
    tstart = time.time()
    #Wait 2xtimes the expected measurment time to check if conversion ready flag shows up
    while not ina260.conversionready and (time.time() - tstart) < (2 * expectedtime):
        time.sleep(0.1)
    dt = time.time() - tstart
    assert dt < 2 * expectedtime, print("Timeout of conversion ready detection")
    print("Conversion Ready detected after {:4.2f} secs".format(dt))

def test_ina260_ConversionreadyWithAlertpin(ina260):
    """
    Test conversion ready flag by using long conversion time and high amount of
    averaging
    """
    #Set INA260 to run long measurement with long conversion time (1.1ms) and highest
    #number of averages (1024) resulting in a measurement time of about 3 seconds
    ina260.reset()
    ina260.avg = 1024
    ina260.measv = True
    ina260.vbusct = 1100
    ina260.measi = False
    ina260.ishct = 1100
    expectedtime = ina260.avg * ina260.vbusct / 1000000
    #Trigger one measurement by setting MODE3 bit to zero
    ina260.meascont = False
    #Configure ALERT pin to be asserted when the conversion ready flag is asserted.
    ina260.alert = ['Conversion Ready']
    ina260.alertlatch = True
    print("\nWaiting {:4.2f} seconds for conversion: ".format(expectedtime), end='')
    tstart = time.time()
    #Wait 2xtimes the expected measurement time to check if ALERT flag shows up
    assert ina260.wait_for_alert_edge(timeout=2*expectedtime), print("Timeout of conversion ready detection")
    print("Alert Pin State change detected after {:4.2f} secs".format(time.time() - tstart))
    #Test edge detect function to detect conversion ready flag using callbacks
    expectedtime = ina260.avg * ina260.vbusct / 1000000
    conversiondetected = False
    def conversionreadydetected(_):
        nonlocal conversiondetected
        dt = time.time() - tstart
        assert dt < 2 * expectedtime, print("Timeout of conversion ready detection")
        print("Alert Pin State rising edge detected after {:4.2f} secs".format(dt))
        conversiondetected = True
    ina260.alertcallback = conversionreadydetected
    ina260.measi = False
    ina260.alertlatch = True
    print("\nWaiting {:4.2f} seconds for conversion: ".format(expectedtime), end='')
    tstart = time.time()
    time.sleep(2 * expectedtime)
    assert conversiondetected, "Timeout of conversion ready detection"
    ina260.alertcallback = None

def test_ina260_alertflag(ina260):
    """
    Test use of alertflag to detect when alertlimit has been exceeded
    """
    #Set the bus Voltage over-voltage alertflag of the INA260 to a
    #very low value to enable triggering it through the measurement noise
    #with no averaging and shortest measurement time
    ina260.reset()
    ina260.avg = 1
    ina260.vbusct = 140
    ina260.measv = True
    ina260.measi = False
    ina260.ishct = 140
    #Configure ALERT pin to be asserted when there is a bus voltage over voltage.
    ina260.alert = ['Bus Voltage Over Voltage']
    ina260.alertlimit = 0.01
    #Wait 1 sec maximum if the expected measurement time to check if ALERT flag shows up
    assert ina260.wait_for_alert_edge(timeout=1), print("Timeout of conversion ready detection")
    print("Alert Pin State change due to bus overvoltage noise.")
    ina260.alert = ['Bus Voltage Over Voltage']
    ina260.alertlimit = 1
    #Wait 1 sec maximum the expected measurement time to check if ALERT flag shows up
    assert not ina260.wait_for_alert_edge(timeout=1), print("Not expected overvoltage detected")
    print("No anomalous bus overvoltage detected.")


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
    ina260.alert = ['Conversion Ready']
    #Enable mains
    mcp23017.enable("Mains")
    print("Waiting 1sec to stabilize readings after mains switched on")
    time.sleep(2.0)
    print("Measuring....")
    assert ina260.wait_for_alert_edge(timeout='Automatic'), print("Timeout of conversion ready detection")
    effvoltage = ina260.voltage() * sqrt(2)
    assert abs(effvoltage - 12.0) < 0.8
    print("Measurement done")

def test_ina260_configio(ina260):
    """
    Test JSON Attribute writing and reading of INA260 Class
    """
    def test_attr(ina260attr, jsondict, attr):
        matches = [key for key in jsondict.keys() if key.endswith(attr)]
        assert matches != [], 'JSON file does not contain {} attribute'
        assert jsondict[matches[0]] == ina260attr, \
            'JSON file contains wrong {} attribute value, is {} and should be {}'.\
            format(attr, jsondict[matches[0]], ina260attr)

    jsonfile = 'test_ina260.json'
    ina260.WriteConfig(jsonfile)
    with open(jsonfile) as f:
        data = json.load(f)
    test_attr(ina260.address, data, "address")
    test_attr(13, data, "alertpin")
    test_attr(ina260.avg, data, "avg")
    test_attr(ina260.vbusct, data, "vbusct")
    test_attr(ina260.ishct, data, "ishct")
    test_attr(ina260.meascont, data, "meascont")
    test_attr(ina260.measi, data, "measi")
    test_attr(ina260.measv, data, "measv")
    test_attr(220, data, "rdiv1")
    #Change Rdiv1 value in JSON File
    matches = [key for key in data.keys() if key.endswith('rdiv1')]
    assert matches != [], 'JSON file does not contain {} attribute'
    with open(jsonfile, 'r+') as f:
        data = json.load(f)
        data[matches[0]] = 240
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
    #Read in modified INA260 JSON configuration file
    ina260.ReadConfig(jsonfile)
    assert ina260.Rdiv1 == 240, "Configuration file {} incorrectly read.".format(jsonfile)

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
