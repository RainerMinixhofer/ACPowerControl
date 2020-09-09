#pylint: disable=C0103
# -*- coding: utf-8 -*-

"""
Code has been downloaded from http://www.gsurf.de/wp-content/uploads/2012/10/mcp23017.zip.
A description of the usage can be found under http://www.gsurf.de/mcp23017-i2c-mit-python-steuern/
Code has been rewritten by Rainer Minixhofer using properties
"""

import smbus #pylint: disable=E0401

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
    def __init__(self, i2cbus=1, device=0x20, bank=0, pinconfig={\
        "gpioa0":"A2AC1", "gpioa1":"B2AC1", "gpioa2":"K2AC1", "gpioa3":"L2AC2", \
        "gpioa4":"M2AC2", "gpioa5":"N2AC2", "gpioa6":"L2D", "gpioa7":"D2K", \
        "gpiob0":"Mains", "gpiob1":"HalfMains1", "gpiob2":"HalfMains2", \
        "gpiob3":"B2L", "gpiob4":"C2M", "gpiob5":"D2N", "gpiob6":"A2K", "gpiob7":"L2AC1"}):
        self.device = device
        self.bus = smbus.SMBus(i2cbus)
        if bank == 0:
            self.gpioa = {"gpioreg":0x12, "dirreg":0x00, "pureg":0x0c}
            self.gpiob = {"gpioreg":0x13, "dirreg":0x01, "pureg":0x0d}
        else:
            self.gpioa = {"gpioreg":0x09, "dirreg":0x00, "pureg":0x06}
            self.gpiob = {"gpioreg":0x19, "dirreg":0x10, "pureg":0x16}
        self.gpiopins = {}
        for key in pinconfig.keys():
            self.gpiopins.update( { key: pin(self, register=key[:-1], bit=int(key[-1])) } )
        self.pins = {pinconfig[key]: value for key, value in self.gpiopins.items()}

class pin:
    """
    Class to access/control one port of the MCP23017 hardware
    """
    def __init__(self, ioexp, register="gpioa", bit=0):
        self.__ioexp = ioexp
        self.__register = register
        if self.__register == "gpioa":
            self.__ioreg = self.__ioexp.gpioa
        else:
            self.__ioreg = self.__ioexp.gpiob
        self.__gpioregaddr = self.__ioreg["gpioreg"]
        self.__dirregaddr = self.__ioreg["dirreg"]
        self.__puregaddr = self.__ioreg["pureg"]
        self.__bit = bit
        #default to tri state
        self.setx()
    @property
    def bit(self):
        """
        Property bit
        """
        return self.__bit
    @bit.setter
    def bit(self, newbit):
        self.__bit = newbit
    @property
    def gpioregaddr(self):
        """
        Yields address of GPIO Port Register. Read-Only
        """
        return self.__gpioregaddr
    @property
    def dirregaddr(self):
        # """
        # Property dirreg. Controls the direction of the data I/O.
        # When a bit is set, the corresponding pin becomes an
        # input. When a bit is clear, the corresponding pin
        # becomes an output.
        # """
        """
        Yields Address of I/O direction register. Read-Only
        """
        return self.__dirregaddr
    @property
    def puregaddr(self):
        """
        Yields Address of GPIO Pull-Up resistor register. Read-Only
        """
        # Property pureg. The GPPU register controls the pull-up resistors for the
        # port pins. If a bit is set and the corresponding pin is
        # configured as an input, the corresponding port pin is
        # internally pulled up with a 100 kOhm resistor.
        return self.__puregaddr
    def enable(self):
        """
        enables port (setting it to output first)
        """
        self.disable_bit(self.__dirregaddr, self.__bit)
        self.enable_bit(self.__gpioregaddr, self.__bit)
        #print self.value
    def disable(self):
        """
        Disables port (setting it to output first)
        """
        self.disable_bit(self.__dirregaddr, self.__bit)
        self.disable_bit(self.__gpioregaddr, self.__bit)
    def setinput(self):
        """
        Set port as input
        """
        self.enable_bit(self.__dirregaddr, self.__bit)
        self.enable_bit(self.__puregaddr, self.__bit)
    def setx(self):
        """
        Tri state mode, input and pullup resistor off
        """

        self.enable_bit(self.__dirregaddr, self.__bit)
        self.disable_bit(self.__puregaddr, self.__bit)
    def value(self):
        """
        Reads port binary status
        """
        try:
            returnvalue = self.__ioexp.bus.read_byte_data(self.__ioexp.device, \
                                                          self.__gpioregaddr) & 2**self.__bit
        except OSError:
            print("Error reading bus")
            return 3
        if returnvalue == 0:
            return 0
        return 1

    def enable_bit(self, register, bit):
        """
        Enables bit <bit> in register <register>
        """
        try:
            value_old = self.__ioexp.bus.read_byte_data(self.__ioexp.device, register)
            newvalue = value_old | (1<<bit)
        except OSError:
            print("Unable to read bus")
        try:
            self.__ioexp.bus.write_byte_data(self.__ioexp.device, register, newvalue)
        except OSError:
            print("Unable to write bus")
    def disable_bit(self, register, bit):
        """
        Disables bit <bit> in register <register>
        """
        try:
            value_old = self.__ioexp.bus.read_byte_data(self.__ioexp.device, register)
            newvalue = value_old & ~(1<<bit)
        except OSError:
            print("Unable to read bus")
        try:
            self.__ioexp.bus.write_byte_data(self.__ioexp.device, register, newvalue)
        except OSError:
            print("Unable to read bus")
