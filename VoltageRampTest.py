#!/usr/bin/python3
# -*- coding:utf-8 -*-
#pylint: disable=C0103,E0401
"""
Ramps Voltage automatically from 1.5V up to 30V with the 1A Coil configuration
Then a shorter ramp from 1,5V up to 15V with the 2A Coil configuration is done
"""
import time
import math
from MCP23017 import MCP23017
import INA260 #pylint: disable=E0401

def switchsequence(gpa, gpb, Vac):
    """

    Parameters
    ----------
    gpa : hexadecimal
        value to write into gpioa register for relais setting of port gpa.
    gpb : hexadecimal
        value to write into gpiob register for relais setting of port gpb.
    Vac : Integer
        Specifies AC Voltage given by the definition of gpa and gpb ports.

    Returns
    -------
    None.

    """

    #Set relais positions for required voltage and leave mains pin as set
    #Switch each bit in sequence instead of in parallel to reduce disturbance
    #of power supply
    gpb |= 0x01
    for b in range(8):
        if (gpa>>b) & 1 == 1:
            mcp23017.enable(port='a', bit=b)
            time.sleep(0.1)
        else:
            mcp23017.disable(port='a', bit=b)
            time.sleep(0.1)
    mcp23017.enable(port='b', bit=0)
    for b in range(1,8):
        if (gpb>>b) & 1 == 1:
            mcp23017.enable(port='b', bit=b)
            time.sleep(0.1)
        else:
            mcp23017.disable(port='b', bit=b)
            time.sleep(0.1)
    #Readout on voltmeter, wait 1s to get voltage settled and to enable measurement integration
    time.sleep(2.0)
    #Since the output is averaged over 256 samples with 1.1ms sample time we get a total averaging
    #time of 281.6ms which are 14.08 periods at 50Hz. Thus the averaged Result Uav for this
    #one way rectifier circuit should be Uav=Ueff/Sqrt(2). Thus the effective AC Voltage is
    #Ueff,i=Uav*Sqrt(2).
    print("Voltage for ",Vac,"V",ina260.voltage() * math.sqrt(2))
    #Set connecting relais back to off
    for b in range(8):
        mcp23017.disable(port='a', bit=b)
        time.sleep(0.1)
    mcp23017.enable(port='b', bit=0)
    for b in range(1,8):
        mcp23017.disable(port='b', bit=b)
        time.sleep(0.1)
    #Wait till next voltage step execution
    time.sleep(2.0)

#create chip driver with bank=0 mode on address 0x20
mcp23017 = MCP23017(i2cbus=1, device=0x20, bank=0, resetpin=4)
#Set all Pins of GPA and GPB of MCP23017 to output
for bit in range(8):
    mcp23017.disable(port="a", bit=bit)
    mcp23017.disable(port="b", bit=bit)
#Check if the registers have been properly set
print("Direction register of port A: 0x{:02X}".format(mcp23017.getregister("iodira")))
print("Direction register of port B: 0x{:02X}".format(mcp23017.getregister("iodirb")))

#INA260 Power Meter has address 0x20 on I2C Bus #1
#Set Averaging mode for 256 averages at 1.1ms conversion time in continous mode
#measuring Shunt Current and Bus Voltage. Voltage divider resistor is 220kOhm
ina260 = INA260.INA260Controller(avg=256, vbusct=1100, ishct=1100, meascont=True, \
                                 measi=True, measv=True, Rdiv1=220)
ina260.reset()

print("Ramping Voltage from 1.5V up to 30V in 1A coil configuration")
input("Press enter when ready....")

#1.5V/1A
switchsequence(0x0C, 0x06, 1.5)
#3.0V/1A
switchsequence(0x0C, 0x00, 3.0)
#4.5V/1A
switchsequence(0x14, 0x06, 4.5)
#6.0V/1A
switchsequence(0x10, 0x80, 6.0)
#7.5V/1A
switchsequence(0x24, 0x06, 7.5)
#9.0V/1A
switchsequence(0x14, 0x00, 9.0)
#10.5V/1A
switchsequence(0x92, 0x06, 10.5)
#12.0V/1A
switchsequence(0x20, 0x80, 12.0)
#13.5V/1A
switchsequence(0x61, 0x06, 13.5)
#15.0V/1A
switchsequence(0x24, 0x00, 15.0)
#18.0V/1A
switchsequence(0x89, 0x00, 18.0)
#21.0V/1A
switchsequence(0x92, 0x00, 21.0)
#24.0V/1A
switchsequence(0x62, 0x00, 24.0)
#27.0V/1A
switchsequence(0x61, 0x00, 27.0)
#30.0V/1A
switchsequence(0xA1, 0x00, 30.0)
print("Ramping Voltage from 1.5V up to 15V in 2A coil configuration")
#1.5V/2A
switchsequence(0x09, 0x4E, 1.5)
#3.0V/2A
switchsequence(0x09, 0x48, 3.0)
#4.5V/2A
switchsequence(0x11, 0x56, 4.5)
#6.0V/2A
switchsequence(0x12, 0x18, 6.0)
#7.5V/2A
switchsequence(0x21, 0x66, 7.5)
#9.0V/2A
switchsequence(0x50, 0x51, 9.0)
#12.0V/2A
switchsequence(0x22, 0x28, 12.0)
#15.0V/2A
switchsequence(0x21, 0x60, 15.0)

#Switch 220V mains off
mcp23017.disable("Mains")

print("End Test")
