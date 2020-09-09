#pylint: disable=C0103
# -*- coding: utf-8 -*-

"""
Code has been downloaded from http://www.gsurf.de/wp-content/uploads/2012/10/mcp23017.zip.
A description of the usage can be found under http://www.gsurf.de/mcp23017-i2c-mit-python-steuern/
Code has been rewritten by Rainer Minixhofer using properties
"""

import smbus #pylint: disable=E0401

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
    """

    def __init__(self, i2cbus=1, device=0x20, bank=0, pinconfig=defaultpinconfig): #pylint: disable=W0102
        self.device = device
        self.bus = smbus.SMBus(i2cbus)
        if bank == 0:
            self.gpioa = {reg : 2*i for i,reg in enumerate(mcp23017registers)}
            self.gpiob = {reg : 2*i+1 for i,reg in enumerate(mcp23017registers)}
        else:
            self.gpioa = {reg : i for i,reg in enumerate(mcp23017registers)}
            self.gpiob = {reg : i + 0x10 for i,reg in enumerate(mcp23017registers)}
        #Generate a reverse lookup dictionary to look up a pin name specification with
        #the standardized port name and bit number (e.g. C2M -> gpiob4)
        self.gpiopins = {value: key for key,value in pinconfig.items()}
        #Set all pins to tri-state by default
        self.setregister(self.registeraddr("iodira"), 0xFF)
        self.setregister(self.registeraddr("iodirb"), 0xFF)
        self.setregister(self.registeraddr("gppua"), 0x00)
        self.setregister(self.registeraddr("gppub"), 0x00)

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
        Reads content of register named <register>. If bit is not None
        just the value of bit number <bit> ist returned.
        If pin is not None, <register> and <bit> are derived from the pin
        specification. If pin is specified register needs to be specified
        without port spec (without "a" or "b" at the end)
        """
        if pin is not None:
            port, bit = self.name2portbit(pin)
            register = register + port
        try:
            value = self.bus.read_byte_data(self.device, self.registeraddr(register))
        except OSError:
            print("Error reading bus")
            return None
        if bit is not None:
            return (value & 2**bit) >> bit
        return value

    def setregister(self, registeraddr, value=0xFF):
        """
        Sets content of register with address <registeraddr> to value.
        """
        assert (0 <= value <= 0xFF), "Register is 8-bit value. Needs to be in range 0x00..0xFF"
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

    def enable(self, port="a", bit=0, pin=None):
        """
        enables bit <bit> of gpio port <port> (setting it to output first).
        If <pin> is specified (not None) the <port> and <bit> settings are
        derived from the gpiopins dictionary
        """
        if pin is not None:
            port, bit = self.name2portbit(pin)
        self.disable_bit(self.registeraddr("iodir"+port), bit)
        self.enable_bit(self.registeraddr("gpio"+port), bit)

    def disable(self, port="a", bit=0, pin=None):
        """
        Disables bit <bit> of gpio port <port> (setting it to output first)
        If <pin> is specified (not None) the <port> and <bit> settings are
        derived from the gpiopins dictionary
        """
        if pin is not None:
            port, bit = self.name2portbit(pin)
        self.disable_bit(self.registeraddr("iodir"+port), bit)
        self.disable_bit(self.registeraddr("gpio"+port), bit)

    def setinput(self, port="a", bit=0, pin=None):
        """
        Set bit <bit> of gpio port <port> to input
        If <pin> is specified (not None) the <port> and <bit> settings are
        derived from the gpiopins dictionary
        """
        if pin is not None:
            port, bit = self.name2portbit(pin)
        self.enable_bit(self.registeraddr("iodir"+port), bit)
        self.enable_bit(self.registeraddr("gppu"+port), bit)

    def setx(self, port="a", bit=0, pin=None):
        """
        Tri state mode, input and pullup resistor off
        If <pin> is specified (not None) the <port> and <bit> settings are
        derived from the gpiopins dictionary
        """
        if pin is not None:
            port, bit = self.name2portbit(pin)
        self.enable_bit(self.registeraddr("iodir"+port), bit)
        self.disable_bit(self.registeraddr("gppu"+port), bit)

    def value(self, port="a", bit=0, pin=None):
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
