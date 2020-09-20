#!/usr/bin/python3
# -*- coding:utf-8 -*-
#pylint: disable=C0103,E0401
"""
Test Critical 220V Supply Switching to measure Supply Disturbance
"""

import time
import os.path
import subprocess
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

def i2c_addr():
    """
    Test if both I2C devices on bus at 0x20 and 0x40 can be found
    """
    completedprocess = subprocess.run(["i2cdetect", "-y", "1"], \
                                      capture_output=True, text=True, check=False)
    assert completedprocess.stderr==''
    output = completedprocess.stdout.split("\n")[1:]
    output = [line.split()[1:] for line in output]
    output = [item for sublist in output for item in sublist]
    return [int('0x'+item,0) for item in output if item != '--']

def test_supplyDisturbanceMains(mcp23017, ina260):
    """
    Capture measurement data with highest possible rate for 200 samples
    """
    filename = "supplyDisturbanceMainsSamples.txt"
    if os.path.exists(filename):
        os.remove(filename)

    mcp23017.enable("Mains")

    #Set all relais to provide 12.0V (without switching on mains yet)
    mcp23017.setregister("gpioa", value=0x20)
    mcp23017.setregister("gpiob", value=0x80)

    print("Waiting 1sec to stabilize readings after mains switched on")
    time.sleep(1.0)
    print("Measuring....")

    ina260.alert = ['Conversion Ready']

    #Start measurements by taking three initial samples
    samples = []
    for _ in range(3):
        ina260.wait_for_alert_edge(timeout='Automatic')
        samples.append(ina260.voltage())
    #Detect maximum by checking if successive differences of the last three
    #voltage samples change their sign from positive to negative
    #Furthermore ensure that the readings are larger than 1V to prevent
    #trigger through noise
    while not (samples[-1]-samples[-2] < 0 < samples[-2]-samples[-3] and\
               all(s>1.0 for s in samples[-3:])):
        ina260.wait_for_alert_edge(timeout='Automatic')
        samples.append(ina260.voltage())

    mcp23017.disable("Mains")

    assert mcp23017.getregister("gpioa") == 0x20, \
        "Cannot access MCP23017 or register gpioa flipped."
    assert mcp23017.getregister("gpiob") == 0x80, \
        "Cannot access MCP23017 or register gpioa flipped."

    print("Mains at Voltage peak switched off. Waiting for coil to settle.")

    time.sleep(1.0)

    mcp23017.setregister("gpioa", value=0x00)
    assert mcp23017.getregister("gpioa") == 0x00, \
        "Cannot access MCP23017 or register gpioa flipped."
    mcp23017.setregister("gpiob", value=0x00)
    assert mcp23017.getregister("gpiob") == 0x00, \
        "Cannot access MCP23017 or register gpioa flipped."

    print("All relais switched off.")

    logfile = open(filename, 'w')
    logfile.writelines(map(lambda x: str(x)+'\n', samples))
    logfile.close()

    assert os.path.exists(filename)
