#pylint: disable=C0103
# -*- coding: utf-8 -*-

"""
Code has been downloaded from http://www.gsurf.de/wp-content/uploads/2012/10/mcp23017.zip.
A description of the usage can be found under http://www.gsurf.de/mcp23017-i2c-mit-python-steuern/
Code has been rewritten by Rainer Minixhofer using properties
"""

import time
import smbus #pylint: disable=E0401
import RPi.GPIO as GPIO #pylint: disable=E0401

mcp23017registers = ["iodir", "ipol", "gpinten", "defval", "intcon", "iocon",\
                     "gppu", "intf", "intcap", "gpio", "olat"]

defaultpinconfig = {"gpioa0":"A2AC1", "gpioa1":"B2AC1", "gpioa2":"K2AC1", "gpioa3":"L2AC2", \
                    "gpioa4":"M2AC2", "gpioa5":"N2AC2", "gpioa6":"L2D", "gpioa7":"D2K", \
                    "gpiob0":"Mains", "gpiob1":"HalfMains1", "gpiob2":"HalfMains2", \
                    "gpiob3":"B2L", "gpiob4":"C2M", "gpiob5":"D2N", "gpiob6":"A2K", \
                    "gpiob7":"L2AC1"}

class MCP23017:
    """
    Class for accessing the MCP23017 hardware
    Default setting for IOCON.BANK = 0 thus the PORTA and PORTB registers
    have sequential adresses. Changing IOCON.BANK to 1 and the associated
    change in register addresses as described in the datasheet is not supported.
    The class provides the interface to the single pins through the
    pins and gpiopins properties. They are dictionaries which use the pinname
    specified in the pinconfig dictionary and the gpioa/gpiob standard pinname
    respectively.
    The resetpin parameter specifies the BCM port of the Raspberry Pi connected to
    the reset pin of the MCP23017.
    """

    def __init__(self, i2cbus=1, device=0x20, bank=0, pinconfig=defaultpinconfig, resetpin = None): #pylint: disable=W0102,R0913
        self.device = device
        self.bus = smbus.SMBus(i2cbus)
        if bank == 0:
            self.gpioa = {reg : 2*i for i, reg in enumerate(mcp23017registers)}
            self.gpiob = {reg : 2*i+1 for i, reg in enumerate(mcp23017registers)}
        else:
            self.gpioa = {reg : i for i, reg in enumerate(mcp23017registers)}
            self.gpiob = {reg : i + 0x10 for i, reg in enumerate(mcp23017registers)}
        #Make reverse lookup dictionary where one can search the register name by
        #looking up it's address
        self.gpioregs = {reg+"a" : addr for reg, addr in self.gpioa.items()}
        self.gpioregs.update({reg+"b" : addr for reg, addr in self.gpiob.items()})
        self.gpioregs = {v: k for k, v in self.gpioregs.items()}
        #Generate a reverse lookup dictionary to look up a pin name specification with
        #the standardized port name and bit number (e.g. C2M -> gpiob4)
        self.gpiopins = {value: key for key, value in pinconfig.items()}
        #Define class properties from register list
#        for reg in mcp23017registers:
#            setattr(self, reg+"a", self.getregister(reg+"a"))
#            setattr(self, reg+"b", self.getregister(reg+"b"))
        #Initialize port extender by pulling resetpin to low if resetpin is not None
        #According to MCP23017 datasheet the minimul reset puls duration must be 1us
        if resetpin is not None:
            GPIO.setmode(GPIO.BCM)
            #Enable MCP23017 by setting reset pin (connected to BCM4) to high
            GPIO.setup(resetpin, GPIO.OUT)
            GPIO.output(resetpin, GPIO.HIGH)
            #Reset MCP23017 by pulling it for 100us to low.
            #This short timing is very incorrect, but sufficiently longer than 1us
            GPIO.output(resetpin, GPIO.LOW)
            time.sleep(0.1/1000)
            GPIO.output(resetpin, GPIO.HIGH)
        #Set all pins to tri-state by default
        self.setregister("iodira", 0xFF)
        self.setregister("iodirb", 0xFF)
        self.setregister("gppua", 0x00)
        self.setregister("gppub", 0x00)

    def __del__(self):
        GPIO.cleanup()

    def registeraddr(self, register="iodira"):
        """
        Gets address of register named <register>
        """
        assert (register[-1] in ["a", "b"]), "Register Port must be \"a\" or \"b\""
        if register[-1] == "a":
            return self.gpioa[register[:-1]]
        return self.gpiob[register[:-1]]

    def getregister(self, register="iodira", bit=None, pin=None):
        """
        Reads content of register named <register> (if register is a string).
        If <register> is an integer it is interpreted as the register address.
        If bit is not None just the value of bit number <bit> ist returned.
        If pin is not None, <register> and <bit> are derived from the pin
        specification. If pin is specified register needs to be specified
        without port spec (without "a" or "b" at the end)
        """
        #save address of register in local variable if register is specified as string
        #and vice versa if it is specified as int (thus interpreted as address)
        if isinstance(register, str):
            if pin is not None:
                port, bit = self.name2portbit(pin)
                register = register + port
            registeraddr = self.registeraddr(register)
        elif isinstance(register, int):
            registeraddr = register
            register = self.gpioregs[registeraddr]
        else:
            raise TypeError("Register must be string(register name) or integer(register address)")
        try:
            value = self.bus.read_byte_data(self.device, registeraddr)
        except OSError:
            print("Error reading bus")
            return None
        if bit is not None:
            return (value & 2**bit) >> bit
        return value

    def setregister(self, register="iodira", value=0xFF):
        """
        Sets content of register with name <register> (if register is a string)
        and with address <register> (if register is an integer) to value.
        """
        assert (0 <= value <= 0xFF), \
            "Register holds an 8-bit value. Needs to be in range 0x00..0xFF"
        #save address of register in local variable if register is specified as string
        #and vice versa if it is specified as int (thus interpreted as address)
        if isinstance(register, str):
            registeraddr = self.registeraddr(register)
        elif isinstance(register, int):
            registeraddr = register
            register = self.gpioregs[registeraddr]
        else:
            raise TypeError("Register must be string(register name) or integer(register address)")
        try:
            self.bus.write_byte_data(self.device, registeraddr, value)
        except OSError:
            print("Unable to write bus")

    def enable_bit(self, registeraddr, bit=0):
        """
        Enables bit <bit> in register with address <registeraddr>
        """
        assert (bit in range(8)), "Bit must be in the range 0..7"
        try:
            value_old = self.bus.read_byte_data(self.device, registeraddr)
            newvalue = value_old | (1<<bit)
        except OSError:
            print("Unable to read bus")
        if newvalue != value_old:
            try:
                self.bus.write_byte_data(self.device, registeraddr, newvalue)
            except OSError:
                print("Unable to write bus")

    def disable_bit(self, registeraddr, bit=0):
        """
        Disables bit <bit> in register with address <registeraddr>
        """
        assert (bit in range(8)), "Bit must be in the range 0..7"
        try:
            value_old = self.bus.read_byte_data(self.device, registeraddr)
            newvalue = value_old & ~(1<<bit)
        except OSError:
            print("Unable to read bus")
        if newvalue != value_old:
            try:
                self.bus.write_byte_data(self.device, registeraddr, newvalue)
            except OSError:
                print("Unable to read bus")

    def name2portbit(self, pin):
        """
        Helper function to look up the standardized <port> and <bit> settings from
        the name of the pin assigned in the pinconfig dictionary
        """

        port, bit = self.gpiopins[pin][-2], int(self.gpiopins[pin][-1])
        assert (port in ["a", "b"]), "Register Port must be \"a\" or \"b\" and not {}".format(port)
        assert (bit in range(8)), "Bit must be in the range 0..7 is {}".format(bit)

        return port, bit

    def enable(self, pin=None, port="a", bit=0):
        """
        enables bit <bit> of gpio port <port> (setting it to output first).
        If <pin> is specified (not None) the <port> and <bit> settings are
        derived from the gpiopins dictionary
        """
        if pin is not None:
            port, bit = self.name2portbit(pin)
        self.disable_bit(self.registeraddr("iodir"+port), bit)
        self.enable_bit(self.registeraddr("gpio"+port), bit)

    def disable(self, pin=None, port="a", bit=0):
        """
        Disables bit <bit> of gpio port <port> (setting it to output first)
        If <pin> is specified (not None) the <port> and <bit> settings are
        derived from the gpiopins dictionary
        """
        if pin is not None:
            port, bit = self.name2portbit(pin)
        self.disable_bit(self.registeraddr("iodir"+port), bit)
        self.disable_bit(self.registeraddr("gpio"+port), bit)

    def setinput(self, pin=None, port="a", bit=0):
        """
        Set bit <bit> of gpio port <port> to input
        If <pin> is specified (not None) the <port> and <bit> settings are
        derived from the gpiopins dictionary
        """
        if pin is not None:
            port, bit = self.name2portbit(pin)
        self.enable_bit(self.registeraddr("iodir"+port), bit)
        self.enable_bit(self.registeraddr("gppu"+port), bit)

    def setx(self, pin=None, port="a", bit=0):
        """
        Tri state mode, input and pullup resistor off
        If <pin> is specified (not None) the <port> and <bit> settings are
        derived from the gpiopins dictionary
        """
        if pin is not None:
            port, bit = self.name2portbit(pin)
        self.enable_bit(self.registeraddr("iodir"+port), bit)
        self.disable_bit(self.registeraddr("gppu"+port), bit)

    def value(self, pin=None, port="a", bit=0):
        """
        Reads port binary status
        If <pin> is specified (not None) the <port> and <bit> settings are
        derived from the gpiopins dictionary
        """
        if pin is not None:
            port, bit = self.name2portbit(pin)
        try:
            returnvalue = self.bus.read_byte_data(self.device, \
                                                  self.registeraddr("gpio"+port)) & 2**bit
        except OSError:
            print("Error reading bus")
            return 3
        if returnvalue == 0:
            return 0
        return 1
