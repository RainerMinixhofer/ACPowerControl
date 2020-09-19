#!/usr/bin/python3
# -*- coding:utf-8 -*-
#pylint: disable=C0103,E0401,R0912
"""
Test access to MCP23017 port expander through MCP23017 class
"""
import time
import pytest
import inflect
from MCP23017 import MCP23017


@pytest.fixture(name="mcp23017")
def fixture_mcp23017():
    """
    create chip driver with bank=0 mode on address 0x20, reset it to initialize
    via GPIO pin 4 of Raspi
    """
    portexpander = MCP23017(i2cbus=1, device=0x20, bank=0, resetpin=4)
    yield portexpander
    del portexpander

def test_mcp23017_registeraccess(mcp23017):
    """
    Test several register access methods
    """
    assert mcp23017.getregister("iodira") == 0xFF
    assert mcp23017.getregister("iodirb") == 0xFF
    assert mcp23017.getregister(register="iodir", pin="Mains") == 1

    mcp23017.disable("Mains")
    assert mcp23017.getregister(register="iodir", pin="Mains") == 0
    assert mcp23017.getregister("iodira") == 0xFF
    assert mcp23017.getregister("iodirb") == 0xFE

    #configure all pins of both ports as outputs (bitwise)
    for bit in range(8):
        mcp23017.disable(port="a", bit=bit)
        mcp23017.disable(port="b", bit=bit)
    assert mcp23017.getregister("iodira") == 0x00
    assert mcp23017.getregister("iodirb") == 0x00

    #Other method to set all Pins of GPA and GPB of MCP23017 to output
    mcp23017.setregister("iodira", value=0xFF)
    mcp23017.setregister("iodirb", value=0xFF)
    assert mcp23017.getregister("iodira") == 0xFF
    assert mcp23017.getregister("iodirb") == 0xFF
    mcp23017.setregister("iodira", value=0x00)
    mcp23017.setregister("iodirb", value=0x00)
    assert mcp23017.getregister("iodira") == 0x00
    assert mcp23017.getregister("iodirb") == 0x00

def test_mcp23017_relaisswitching(mcp23017):
    """
    Demo how to access Relais cards through MCP23017 port expander
    Switch one and multiple channels to see if there are any EMC issues
    The mains pin remains off to prevent any EMC coming from powering the
    Transformer
    """

    p = inflect.engine()

    waittime = 0.5 # in seconds

    print("Test writing into GPIOA/GPIOB registers using enable/disable")
    for tst in range(1, 8):
        if tst == 1:
            tststrng = "single"
        else:
            tststrng = p.number_to_words(tst) + " adjacent"

        print("Switching every {} relais in sequence every {} seconds using enable/disable..."\
              .format(tststrng, round(waittime, 1)))
        print("First Port GPA")
        for bit in range(9-tst):
            for rel in range(tst):
                mcp23017.enable(port="a", bit=bit+rel)
            regval = mcp23017.getregister("gpioa")
            shouldval = sum([1<<i for i in range(bit, tst+bit)])
            assert regval == shouldval,\
                "Getregister on GPIOB should return 0x{:02X} but returns {:02X}."\
                    .format(shouldval, regval)
            time.sleep(waittime)
            for rel in range(tst):
                mcp23017.disable(port="a", bit=bit+rel)
            regval = mcp23017.getregister("gpioa")
            shouldval = 0x00
            assert regval == shouldval,\
                "Getregister on GPIOB should return 0x{:02X} but returns {:02X}."\
                    .format(shouldval, regval)
        print("Then Port GPB (without mains pin GPB0)")
        for bit in range(1, 9-tst):
            for rel in range(tst):
                mcp23017.enable(port="b", bit=bit+rel)
            regval = mcp23017.getregister("gpiob")
            shouldval = sum([1<<i for i in range(bit, tst+bit)])
            assert regval == shouldval,\
                "Getregister on GPIOB should return 0x{:02X} but returns {:02X}."\
                    .format(shouldval, regval)
            time.sleep(waittime)
            for rel in range(tst):
                mcp23017.disable(port="b", bit=bit+rel)
            regval = mcp23017.getregister("gpiob")
            shouldval = 0x00
            assert regval == shouldval,\
                "Getregister on GPIOB should return 0x{:02X} but returns {:02X}."\
                    .format(shouldval, regval)
    print("Test writing into GPIOA/GPIOB registers using setregister")
    for tst in range(1, 8):
        if tst == 1:
            tststrng = "single"
        else:
            tststrng = p.number_to_words(tst) + " adjacent"

        print("Switching every {} relais in sequence every {} seconds using setregister..."\
              .format(tststrng, round(waittime, 1)))
        print("First Port GPA")
        for bit in range(9-tst):
            regval = sum([1<<i for i in range(bit, tst+bit)])
            mcp23017.setregister("gpioa", regval)
            assert mcp23017.getregister("gpioa") == regval
            time.sleep(waittime)
            for rel in range(tst):
                mcp23017.disable(port="a", bit=bit+rel)
            assert mcp23017.getregister("gpioa") == 0x00
        print("Then Port GPB (without mains pin GPB0)")
        for bit in range(1, 9-tst):
            regval = sum([1<<i for i in range(bit, tst+bit)])
            mcp23017.setregister("gpiob", regval)
            assert mcp23017.getregister("gpiob") == regval
            time.sleep(waittime)
            for rel in range(tst):
                mcp23017.disable(port="b", bit=bit+rel)
            assert mcp23017.getregister("gpiob") == 0x00
    print("End Test")
