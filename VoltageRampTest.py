#!/usr/bin/python3
# -*- coding:utf-8 -*-
#pylint: disable=C0103,E0401
"""
Ramps Voltage automatically from 1.5V up to 30V with the 1A Coil configuration
Then a shorter ramp from 1,5V up to 15V with the 2A Coil configuration is done
"""
import time
from math import sqrt
from MCP23017 import MCP23017
import INA260 #pylint: disable=E0401

#Define voltage ladder one gets from the valid combination of the 3V, and 2x6V
#secondary coils of the transformer for low current (1A) and the high current
#(2A) option
validV1A = []
for i in range(10):
    validV1A.append(1.5 * (i+1))
for i in range(5):
    validV1A.append(3.0 * (i+1) + validV1A[9])
validV2A = []
for i in range(6):
    validV2A.append(1.5 * (i+1))
for i in range(2):
    validV2A.append(3.0 * (i+1) + validV2A[5])

#Define the corresponding register settings for the required connections
#for the above defined voltage ladder. The MSB byte is port A the LSB byte is port B
reg1A = [0x0C06, 0x0C00, 0x1406, 0x1080, 0x2406, 0x1400, 0x9206, 0x2080, 0x6106, \
         0x2400, 0x8900, 0x9200, 0x6200, 0x6100, 0xA100]
dict1A = dict(zip(validV1A, reg1A))
reg2A = [0x094E, 0x0948, 0x1156, 0x1218, 0x2166, 0x1150, 0x2228, 0x2160]
dict2A = dict(zip(validV2A, reg2A))

def voltage2registers(voltage, highcurrent=False):
    """
    Converts the specified ac voltage in the tuple <allowed Vac>, <register a> and
    <register b> and returns the values
    """
    #Limit voltage to allowed values. Take closest allowed value from validVxA lists
    voltage = min(validV2A if highcurrent else validV1A, key=lambda x: abs(x-voltage))
    regs = dict2A[voltage] if highcurrent else dict1A[voltage]
    return voltage, regs >> 8, regs & 0xFF

def switchsequence(portextender, powermeter, Vac, highcurrent=False):
    """

    Parameters
    ----------
    highcurrent : Boolean
        If True the register settings for 2A configuration is returned, if
        False then the register setting for 1A is returned
    portextender, powermeter : object
        Objects for the handling of the portextender and the powermeter respectively
    Vac : Integer
        Specifies AC Voltage given by the definition of gpa and gpb ports.

    Returns
    -------
    None

    """

    #Get the required register settings for specified voltage Vac
    Vac, gpa, gpb = voltage2registers(Vac, highcurrent=highcurrent)
    #Set relais positions for required voltage and leave mains pin off
    #Then switch on mains
    portextender.setregister("gpioa", gpa)
    portextender.setregister("gpiob", gpb)
    portextender.enable('Mains')
    time.sleep(1.0)
    #Readout on voltmeter, wait 1s to get voltage settled and to enable measurement integration
    #Since we have a single rectifier in the sensing circuit
    #The AC effective voltage measured is sqrt(2) times lower than the
    #effective voltage
    effvoltage = 0
    count = 0
    while abs(effvoltage-Vac)>1.0 and (count<1):
        print("Measuring....")
        powermeter.alert = ['Conversion Ready']
        assert powermeter.wait_for_alert_edge(timeout='Automatic'), \
        print("Timeout of conversion ready detection")
        effvoltage = powermeter.voltage() * sqrt(2)
        print("Voltage setting: {:4.1f}V ({:5.2f}V measured)".format(Vac, effvoltage))
        count += 1
    #Wait for voltage peak to minimize EMC when switching off mains
    powermeter.wait_for_voltage_peak()
    #Switch mains off
    portextender.disable('Mains')
    time.sleep(1.0)
    portextender.setregister("gpioa", 0x00)
    portextender.setregister("gpiob", 0x00)
    time.sleep(1.0)
#    portextender.reset()
#    portextender.all_to_output()

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
#we take a long conversion time of 1.1ms together with the highest
#number of averaging samples in continous mode, which should yield sufficient accuracy
#to get a good estimate for the AC effective voltage
#Measuring only Bus Voltage. Voltage divider resistor is 220kOhm
#ina260 = INA260.INA260Controller(alertpin=13, avg=1024, vbusct=1100, meascont=True, \
#                                 measi=False, measv=True, Rdiv1=220, alert = ['Conversion Ready'])
ina260 = INA260.INA260Controller(alertpin=13, avg=1024, vbusct=1100, ishct=140, meascont=True, \
                                 measi=False, measv=True, Rdiv1=220, Rvbus=340)

print("Ramping Voltage from 1.5V up to 30V in 1A coil configuration")
input("Press enter when ready....")

for vac in validV1A:
    switchsequence(mcp23017, ina260, vac, highcurrent=False)
print("Ramping Voltage from 1.5V up to 15V in 2A coil configuration")
for vac in validV2A:
    switchsequence(mcp23017, ina260, vac, highcurrent=True)

del mcp23017
del ina260

print("End of Voltage Ramp")
