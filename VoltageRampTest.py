#!/usr/bin/python3
# -*- coding:utf-8 -*-
#pylint: disable=C0103,E0401
"""
Ramps Voltage automatically from 1.5V up to 30V with the 1A Coil configuration
Then a shorter ramp from 1,5V up to 15V with the 2A Coil configuration is done
"""
import time
import math
import RPi.GPIO as GPIO
import smbus

def switchsequence(gpa, gpb, Vac):
    """

    Parameters
    ----------
    gpa : hexadecimal
        value to write into 0x14 register for relais setting of port gpa.
    gpb : hexadecimal
        value to write into 0x15 register for relais setting of port gpb.
    Vac : Integer
        Specifies AC Voltage given by the definition of gpa and gpb ports.

    Returns
    -------
    None.

    """

    #Set relais positions for required voltage (with 220V mains still of)
    bus.write_byte_data(reladdress, 0x14, gpa)
    bus.write_byte_data(reladdress, 0x15, gpb)
    #Wait for 100ms to settle any relais bouncing
    time.sleep(0.1)
    #Switch 220V mains on
    bus.write_byte_data(reladdress, 0x15, gpb+1)
    #Readout on voltmeter, wait 1s to get voltage settled and to enable measurement integration
    time.sleep(1.0)
    #Read voltage register 0x02 and convert to mV (multiply by 1.25).
    #Since the output is averaged over 256 samples with 1.1ms sample time we get a total averaging time of 281.6ms which
    #are 14.08 periods at 50Hz. Thus the averaged Result Uav for this one way rectifier circuit should
    #be Uav=Ueff/Sqrt(2). Thus the effective AC Voltage is Ueff,i=Uav*Sqrt(2)
    #The Cicuit has a voltage divider with R1=220kOhm R2=380kOhm, thus the input voltage of the divider is Ueff=Ueff,i*(R1+R2)/R2
    #and thus multiplied by (R1+R2)/R2
    voltage = bend2lend(bus.read_word_data(metaddress, 0x02)) * 1.25 * math.sqrt(2) * (220+380)/220
    print("Voltage for ",Vac,"V",voltage)
    time.sleep(1.0)
    #Switch off 220V again
    bus.write_byte_data(reladdress, 0x15, gpb)
    #Wait for 1sec to let magnetic power in coil decay over varistor
    time.sleep(1.0)
    #Set remaining relais back to off
    bus.write_byte_data(reladdress, 0x14, 0x00)
    bus.write_byte_data(reladdress, 0x15, 0x00)
    #Wait till next voltage step execution
    time.sleep(2.0)

def bend2lend(value):
    """
    Converts integer value <value> from big endian to little endian and vice versa
    """
    result = ((value&(255<<8))>>8)|((value&255)<<8)
    if result > 32767:
        result -= 1
        result = -((~result) & 65535)
    return result

GPIO.setmode(GPIO.BCM)
#Initialize I2C Bus #1
bus = smbus.SMBus(1)
#Enable MCP23017 by setting reset pin (connected to BCM4) to high
RESET_PIN = 4
GPIO.setup(RESET_PIN, GPIO.OUT, initial=GPIO.HIGH)

#MCP23017 Port Expander has address 0x20 on I2C Bus #1
reladdress = 0x20
#Set all Pins of GPA and GPB of MCP23017 to output
bus.write_byte_data(reladdress, 0x00, 0x00)
bus.write_byte_data(reladdress, 0x01, 0x00)
#Check if the registers have been properly set
print("Register setting at 0x00:", bus.read_byte_data(reladdress, 0x00))
print("Register setting at 0x01:", bus.read_byte_data(reladdress, 0x01))

#INA260 Power Meter has address 0x20 on I2C Bus #1
metaddress = 0x40
#Set Averaging mode for 256 averages at 1.1ms conversion time in continous mode measuring Shunt Current and Bus Voltage
#We write the binary data b0110101100100111=0x6B27 in big endian form into the configuration register 0x00
bus.write_word_data(metaddress, 0x00, 0x276B)

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
#switchsequence(0x61, 0x06, 13.5)
#15.0V/1A
#switchsequence(0x24, 0x00, 15.0)
#18.0V/1A
#switchsequence(0x89, 0x00, 18.0)
#21.0V/1A
#switchsequence(0x92, 0x00, 21.0)
#24.0V/1A
#switchsequence(0x62, 0x00, 24.0)
#27.0V/1A
#switchsequence(0x61, 0x00, 27.0)
#30.0V/1A
#switchsequence(0xA1, 0x00, 30.0)
print("Ramping Voltage from 1.5V up to 15V in 2A coil configuration")
#1.5V/2A
#switchsequence(0x09, 0x4E, 1.5)
#3.0V/2A
#switchsequence(0x09, 0x48, 3.0)
#4.5V/2A
#switchsequence(0x11, 0x56, 4.5)
#6.0V/2A
#switchsequence(0x12, 0x18, 6.0)
#7.5V/2A
#switchsequence(0x21, 0x66, 7.5)
#9.0V/2A
#switchsequence(0x50, 0x51, 9.0)
#12.0V/2A
#switchsequence(0x22, 0x28, 12.0)
#15.0V/2A
#switchsequence(0x21, 0x60, 15.0)
print("End Test")

