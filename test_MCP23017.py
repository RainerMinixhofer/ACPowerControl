#!/usr/bin/python3
# -*- coding:utf-8 -*-
#pylint: disable=C0103,E0401
"""
Test access to MCP23017 port expander through MCP23017 class
"""
import pytest
from MCP23017 import MCP23017


@pytest.fixture
def mcp23017():
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
        mcp23017.disable(port="a",bit=bit)
        mcp23017.disable(port="b",bit=bit)
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
 