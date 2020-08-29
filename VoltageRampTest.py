#!/usr/bin/python3
# -*- coding:utf-8 -*-
#pylint: disable=C0103,E0401
"""
Ramps Voltage automatically from 1.5V up to 30V with the 1A Coil configuration
Then a shorter ramp from 1,5V up to 15V with the 2A Coil configuration is done
"""
import time
import RPi.GPIO as GPIO
import smbus

def switchsequence(gpa, gpb):
    """

    Parameters
    ----------
    gpa : hexadecimal
        value to write into 0x14 register for relais setting of port gpa.
    gpb : TYPE
        value to write into 0x15 register for relais setting of port gpb.

    Returns
    -------
    None.

    """

    #Set relais positions for required voltage (with 220V mains still of)
    bus.write_byte_data(address, 0x14, gpa)
    bus.write_byte_data(address, 0x15, gpb)
    #Wait for 100ms to settle any relais bouncing
    time.sleep(1.0)
    #Switch 220V mains on
    bus.write_byte_data(address, 0x15, gpb+1)
    #Wait 1 second to enable readout on voltmeter
    time.sleep(5.0)
    #Set all relais back to off
    bus.write_byte_data(address, 0x14, 0x00)
    bus.write_byte_data(address, 0x15, 0x00)
    #Wait for 100ms to settle any relais bouncing
    time.sleep(1.0)


GPIO.setmode(GPIO.BCM)
#Enable MCP23017 by setting reset pin (connected to BCM4) to high
RESET_PIN = 4
GPIO.setup(RESET_PIN, GPIO.OUT, initial=GPIO.HIGH)

#Initialize I2C Bus #1 for MCP23017 with address 0x20
address = 0x20
bus = smbus.SMBus(1)
#Set all Pins of GPA and GPB of MCP23017 to output
bus.write_byte_data(address, 0x00, 0x00)
bus.write_byte_data(address, 0x01, 0x00)
#Check if the registers have been properly set
print("Register setting at 0x00:", bus.read_byte_data(address, 0x00))
print("Register setting at 0x01:", bus.read_byte_data(address, 0x01))
print("Ramping Voltage from 1.5V up to 30V in 1A coil configuration")
input("Connect Voltmeter to read voltage and press enter when ready....")
#1.5V/1A
switchsequence(0x0C, 0x06)
#3.0V/1A
switchsequence(0x0C, 0x00)
#4.5V/1A
switchsequence(0x14, 0x06)
#6.0V/1A
switchsequence(0x10, 0x80)
#7.5V/1A
switchsequence(0x24, 0x06)
#9.0V/1A
switchsequence(0x14, 0x00)
#10.5V/1A
switchsequence(0x92, 0x06)
#12.0V/1A
switchsequence(0x20, 0x80)
#13.5V/1A
switchsequence(0x61, 0x06)
#15.0V/1A
switchsequence(0x24, 0x00)
#18.0V/1A
switchsequence(0x89, 0x00)
#21.0V/1A
switchsequence(0x92, 0x00)
#24.0V/1A
switchsequence(0x62, 0x00)
#27.0V/1A
switchsequence(0x61, 0x00)
#30.0V/1A
switchsequence(0xA1, 0x00)
print("Ramping Voltage from 1.5V up to 15V in 2A coil configuration")
#1.5V/2A
switchsequence(0x09, 0x4E)
#3.0V/2A
switchsequence(0x09, 0x48)
#4.5V/2A
switchsequence(0x11, 0x56)
#6.0V/2A
switchsequence(0x12, 0x18)
#7.5V/2A
switchsequence(0x21, 0x66)
#9.0V/2A
switchsequence(0x50, 0x51)
#12.0V/2A
switchsequence(0x22, 0x28)
#15.0V/2A
switchsequence(0x21, 0x60)
print("End Test")
