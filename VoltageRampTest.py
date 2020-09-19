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

def switchsequence(portextender, powermeter, gpa, gpb, Vac):
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

    #Set relais positions for required voltage and leave mains pin off
    #Then switch on mains
    portextender.setregister("gpioa", gpa)
    portextender.setregister("gpiob", gpb)
    portextender.enable('Mains')
    #Readout on voltmeter, wait 1s to get voltage settled and to enable measurement integration
    time.sleep(2.0)
    #Since the output is averaged over 256 samples with 1.1ms sample time we get a total averaging
    #time of 281.6ms which are 14.08 periods at 50Hz. Thus the averaged Result Uav for this
    #one way rectifier circuit should be Uav=Ueff/Sqrt(2). Thus the effective AC Voltage is
    #Ueff,i=Uav*Sqrt(2).
    # TODO: Enter averaging routine for effective voltage here
    print("Voltage for ", Vac, "V", powermeter.voltage() * math.sqrt(2))
    #Switch mains off
    # TODO: Enter wait for voltage peak here
    portextender.disable('Mains')
    time.sleep(0.5)
    portextender.reset()
    portextender.all_to_output()

#create chip driver with bank=0 mode on address 0x20
mcp23017 = MCP23017(i2cbus=1, device=0x20, bank=0, resetpin=4)
#Set all Pins of GPA and GPB of MCP23017 to output and disabled
mcp23017.all_to_output()
#Check if the registers have been properly set
assert mcp23017.getregister("iodira") == 0x00, \
    "Direction of GPIOA registers not properly set. Is {}, and should be{}".\
        format(mcp23017.getregister("iodira"), 0x00)
assert mcp23017.getregister("iodirb") == 0x00, \
    "Direction of GPIOB registers not properly set. Is {}, and should be{}".\
        format(mcp23017.getregister("iodirb"), 0x00)

#INA260 Power Meter has address 0x20 on I2C Bus #1
#Set Averaging mode for 256 averages at 1.1ms conversion time in continous mode
#measuring Shunt Current and Bus Voltage. Voltage divider resistor is 220kOhm
ina260 = INA260.INA260Controller(avg=256, vbusct=1100, meascont=True, \
                                 measi=False, measv=True, Rdiv1=220)

print("Ramping Voltage from 1.5V up to 30V in 1A coil configuration")
input("Press enter when ready....")

#1.5V/1A
switchsequence(mcp23017, ina260, 0x0C, 0x06, 1.5)
#3.0V/1A
switchsequence(mcp23017, ina260, 0x0C, 0x00, 3.0)
#4.5V/1A
switchsequence(mcp23017, ina260, 0x14, 0x06, 4.5)
#6.0V/1A
switchsequence(mcp23017, ina260, 0x10, 0x80, 6.0)
#7.5V/1A
switchsequence(mcp23017, ina260, 0x24, 0x06, 7.5)
#9.0V/1A
switchsequence(mcp23017, ina260, 0x14, 0x00, 9.0)
#10.5V/1A
switchsequence(mcp23017, ina260, 0x92, 0x06, 10.5)
#12.0V/1A
switchsequence(mcp23017, ina260, 0x20, 0x80, 12.0)
#13.5V/1A
switchsequence(mcp23017, ina260, 0x61, 0x06, 13.5)
#15.0V/1A
switchsequence(mcp23017, ina260, 0x24, 0x00, 15.0)
#18.0V/1A
switchsequence(mcp23017, ina260, 0x89, 0x00, 18.0)
#21.0V/1A
switchsequence(mcp23017, ina260, 0x92, 0x00, 21.0)
#24.0V/1A
switchsequence(mcp23017, ina260, 0x62, 0x00, 24.0)
#27.0V/1A
switchsequence(mcp23017, ina260, 0x61, 0x00, 27.0)
#30.0V/1A
switchsequence(mcp23017, ina260, 0xA1, 0x00, 30.0)
print("Ramping Voltage from 1.5V up to 15V in 2A coil configuration")
#1.5V/2A
switchsequence(mcp23017, ina260, 0x09, 0x4E, 1.5)
#3.0V/2A
switchsequence(mcp23017, ina260, 0x09, 0x48, 3.0)
#4.5V/2A
switchsequence(mcp23017, ina260, 0x11, 0x56, 4.5)
#6.0V/2A
switchsequence(mcp23017, ina260, 0x12, 0x18, 6.0)
#7.5V/2A
switchsequence(mcp23017, ina260, 0x21, 0x66, 7.5)
#9.0V/2A
switchsequence(mcp23017, ina260, 0x50, 0x51, 9.0)
#12.0V/2A
switchsequence(mcp23017, ina260, 0x22, 0x28, 12.0)
#15.0V/2A
switchsequence(mcp23017, ina260, 0x21, 0x60, 15.0)

del mcp23017
del ina260

print("End of Voltage Ramp")
