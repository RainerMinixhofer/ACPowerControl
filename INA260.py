#pylint: disable=C0103,R0913,R0902,R0904
"""
Driver for accessing INA260 Power Meter Chip from Texas Instruments
Based on the implementation by Josh Veitch-Michaelis at https://github.com/jveitchmichaelis/ina260
Added Functionality (Setting averaging parameters and integration time) by Rainer Minixhofer
"""

import struct
import smbus #pylint: disable=E0401

PCA_AUTOINCREMENT_OFF = 0x00
PCA_AUTOINCREMENT_ALL = 0x80
PCA_AUTOINCREMENT_INDIVIDUAL = 0xA0
PCA_AUTOINCREMENT_CONTROL = 0xC0
PCA_AUTOINCREMENT_CONTROL_GLOBAL = 0xE0

REG_CONFIG = 0x00
REG_CURRENT = 0x01
REG_BUS_VOLTAGE = 0x02
REG_POWER = 0x03
REG_MASK_ENABLE = 0x06
REG_ALERT = 0x07
REG_MANUFACTURER_ID = 0xFE
REG_DIE_ID = 0xFF

RST = 15
AVG2 = 11
AVG1 = 10
AVG0 = 9
AVG = [1, 4, 16, 64, 128, 256, 512, 1024] # average sample settings
VBUSCT2 = 8
VBUSCT1 = 7
VBUSCT0 = 6
CT = [140, 204, 332, 588, 1100, 2116, 4156, 8244] # Vbus and Ishunt conversion time settings in  us
ISHCT2 = 5
ISHCT1 = 4
ISHCT0 = 3
MODE3 = 2
MODE2 = 1
MODE1 = 0

OCL = 15
UCL = 14
BOL = 13
BUL = 12
POL = 11
CNVR = 10
ALERT = ['Conversion Ready', 'Power Over Limit', 'Bus Voltage Under Voltage', \
         'Bus Voltage Over Voltage', 'Under Current Limit', 'Over Current Limit']
AFF = 4
CVRF = 3
OVF = 2
APOL = 1
LEN = 0

A_per_Bit = 1.25 / 1000
V_per_Bit = 1.25 / 1000
W_per_Bit = 10.0 / 1000

class INA260Controller:
    """
    Driver Class for TI INA260 Controller
    
    address... Specifies I2C address of hardware
    channel... Specifies I2C channel of hardware
    The following settings can be found in the INA260 datasheet
    avg....... Number of samples which get averaged before conversion ready is signaled
    vbusct.... Vbus conversion time in us
    ishct..... Ish conversion time in us
    meascont.. Measure continuiously (True) or triggered(False)
    measv..... True if Vbus to be measured
    measi..... True if Ish to be measured
    alert..... Assign list of states given in ALERT list. Only one out of the 
               over or under limits are allowed to be specified together with 
               the conversion ready alert
    alertpol.. Polarity of alert pin
    alertlatch If 1 the alert stays latched if 0 it clears as soon as the alert criterion
               is not fulfilled anymore
    alertlimit Specifies the alert limit in units of the alert selected in <alert>.
               For Voltage or Power limits this specifies the true voltage measured
               and not the Vbus pin voltage.
    Rdiv1..... If a series resistor is connected to Vbus this specifies the value
               of the resistor to calculate the measured voltage based on the
               voltage divider rule. The voltage divider consists of Rdiv1
               and Rvbus (see next). Is zero by default yielding no voltage
               divider.
    Rvbus..... Typical value for the VBUS input impedance as per datasheet for
               calculating the measured voltage when a series resistor is used.
    
    """

    def __init__(self, address=0x40, channel=1, avg=1, vbusct=1100, ishct=1100, \
                 meascont=True, measv=True, measi=True, \
                 alert=None, alertpol=0, alertlatch=0, alertlimit=0, Rdiv1=0, Rvbus=380):
        self.i2c_channel = channel
        self.bus = smbus.SMBus(self.i2c_channel)
        self.address = address
        self.__avg = avg
        self.__vbusct = vbusct
        self.__ishct = ishct
        self.__meascont = meascont
        self.__measv = measv
        self.__measi = measi
        self.__alert = alert
        self.__alertpol = alertpol
        self.__alertlatch = alertlatch
        self.__alertlimit = alertlimit
        self.__rdiv1 = Rdiv1
        self.__rvbus = Rvbus
        self.__fvdiv = Rvbus / (Rdiv1 + Rvbus) # Voltage divider factor Vbus/Vmeas

    @property
    def avg(self):
        """
        Method avg holding the number of average per measurement of INA260
        """
        return self.__avg
    @avg.setter
    def avg(self, avg):
        assert (avg in AVG), "avg is not in allowed list of values: {}".format(AVG)
        creg = self._read(REG_CONFIG)
        creg = self.__setbits(creg, [AVG0, AVG1, AVG2], AVG.index(avg))
        self._write(REG_CONFIG, creg)
        self.__avg = avg

    @property
    def vbusct(self):
        """
        Method vbusct holding the Bus Voltage Conversion Time Setting of INA260
        """
        return self.__vbusct
    @vbusct.setter
    def vbusct(self, vbusct):
        assert (vbusct in CT), "vbusct is not in allowed list of values: {}".format(CT)
        creg = self._read(REG_CONFIG)
        creg = self.__setbits(creg, [VBUSCT0, VBUSCT1, VBUSCT2], CT.index(vbusct))
        self._write(REG_CONFIG, creg)
        self.__vbusct = vbusct

    @property
    def ishct(self):
        """
        Method ishct holding the Shunt Current Conversion Time Setting of INA260
        """
        return self.__ishct
    @ishct.setter
    def ishct(self, ishct):
        assert (ishct in CT), "ishct is not in allowed list of values: {}".format(CT)
        creg = self._read(REG_CONFIG)
        creg = self.__setbits(creg, [ISHCT0, ISHCT1, ISHCT2], CT.index(ishct))
        self._write(REG_CONFIG, creg)
        self.__ishct = ishct

    @property
    def meascont(self):
        """
        Method meascont holding continous/triggered measurement setting of INA260
        """
        return self.__meascont
    @meascont.setter
    def meascont(self, meascont):
        assert (meascont in [True, False]), "meascont is not boolean"
        creg = self._read(REG_CONFIG)
        creg = self.__setbits(creg, [MODE3], meascont)
        self._write(REG_CONFIG, creg)
        self.__meascont = meascont

    @property
    def measv(self):
        """
        Method measv holding the setting if vbus is measured with INA260
        """
        return self.__measv
    @measv.setter
    def measv(self, measv):
        assert (measv in [True, False]), "measv is not boolean"
        creg = self._read(REG_CONFIG)
        creg = self.__setbits(creg, [MODE2], measv)
        self._write(REG_CONFIG, creg)
        self.__measv = measv

    @property
    def measi(self):
        """
        Method measi holding the setting if ish is measured with INA260
        """
        return self.__measi
    @measi.setter
    def measi(self, measi):
        assert (measi in [True, False]), "measi is not boolean"
        creg = self._read(REG_CONFIG)
        creg = self.__setbits(creg, [MODE1], measi)
        self._write(REG_CONFIG, creg)
        self.__measi = measi

    @property
    def alert(self):
        """
        Method alert specifying if and which alert should be associated
        to the ALERT pin of the INA260
        """
        return self.__alert
    @alert.setter
    def alert(self, alert):
        assert True if alert is None or alert == '' else all(i in ALERT for i in alert), \
            "alert contains not only elements from allowed list of values: {}".format(ALERT)
        mereg = self._read(REG_MASK_ENABLE)
        alerts = 0
        if alert is not None and alert != '':
            alertlist = list(ALERT.index(i) for i in alert)
            #If multiple functions are enabled, the highest significant bit position \
            #Alert Function (D15-D11) takes priority and responds to the Alert Limit Register
            if any(a > 0 for a in alertlist):
                alert = [ALERT[max(alertlist)]]
                alerts = 2**max(alertlist)
            #Conversion Ready flag can be enabled separately
            if any(a == 0 for a in alertlist):
                alerts += 1
                alert.insert(0,ALERT[0])
        mereg = self.__setbits(mereg, [CNVR, POL, BUL, BOL, UCL, OCL], alerts)
        self._write(REG_MASK_ENABLE, mereg)
        self.__alert = alert

    @property
    def alertpol(self):
        """
        Method alertpol specifying the alert polarity bit
        1 = ALERT Pin signal is inverted (active-high open collector)
        0 = ALERT Pin signal is normal (active-low open collector)
        """
        return self.__alertpol
    @alertpol.setter
    def alertpol(self, alertpol):
        assert (alertpol in [0,1]), "alertpol is not in allowed list of values: {}".format([0,1])
        mereg = self._read(REG_MASK_ENABLE)
        mereg = self.__setbits(mereg, [APOL], alertpol)
        self._write(REG_MASK_ENABLE, mereg)
        self.__alertpol = alertpol

    @property
    def alertlatch(self):
        """
        Method alertlatch specifying the alert latch enable bit.
        Configures the latching feature of the ALERT pin and Alert Flag bits.
        1 = Latch enabled
        0 = Transparent
        """
        return self.__alertlatch
    @alertlatch.setter
    def alertlatch(self, alertlatch):
        assert (alertlatch in [0,1]), "alertlatch is not in allowed list of values: {}".\
            format([0,1])
        mereg = self._read(REG_MASK_ENABLE)
        mereg = self.__setbits(mereg, [LEN], alertlatch)
        self._write(REG_MASK_ENABLE, mereg)
        self.__alertlatch = alertlatch

    @property
    def alertlimit(self):
        """
        Method limit specifies the value used to compare to the register selected in the
        Mask/Enable Register to determine if a limit has been exceeded.
        The format for this register will match the format of the register that is
        selected for comparison.
        """
        return self.__alertlimit
    @alertlimit.setter
    def alertlimit(self, alertlimit):
        alertlist = list(ALERT.index(i) for i in self.__alert)
        assert any(a > 0 for a in alertlist), \
            "Alertlimit can just be set if one of the alertflags for voltage, \
current or power has been specified"
        #Convert interpret alertlimit units based on alert setting. Take  first
        #element from alertlist which is not zero
        alertunit = next(val for val in alertlist if val != 0)
        print("Alertunit:", alertunit)
        if alertunit > 3: # Current Unit 1.25mA/bit. Same current through voltage divider
            alertint = round(alertlimit / A_per_Bit)
            alertlimit = alertint * A_per_Bit
        elif alertunit > 1: # Voltage Unit 1.25mV/bit. Voltage divider factor applied
            alertint = round(alertlimit * self.__fvdiv / V_per_Bit)
            alertlimit = alertint * V_per_Bit
        else: #Energy Unit 10mW/bit. Voltage divider factor for bus voltage applied
            alertint = round(alertlimit * self.__fvdiv / W_per_Bit)
            alertlimit = alertint * W_per_Bit
        assert (0 <= alertint <= 0xFFFF), "alertlimit has to be a 16-bit Integer"
        self._write(REG_ALERT, alertint)
        self.__alertlimit = alertlimit

    @property
    def alertflag(self):
        """
        The read only method alertflag.
        While only one Alert Function can be monitored at the ALERT pin at a time, the
        Conversion Ready can also be enabled to assert the ALERT pin. Reading the Alert
        Function Flag following an alert allows the user to determine if the Alert Function
        was the source of the Alert.
        When the Alert Latch Enable bit is set to Latch mode, the Alert Function Flag bit
        clears only when the Mask/Enable Register is read. When the Alert Latch Enable
        bit is set to Transparent mode, the Alert Function Flag bit is cleared following the
        next conversion that does not result in an Alert condition.
        """
        return (self._read(REG_MASK_ENABLE) & self.__bitmask(AFF)) >> AFF

    @property
    def conversionready(self):
        """
        Conversion Ready flag read only method.
        Although the device can be read at any time, and the data from the last conversion
        is available, the Conversion Ready Flag bit is provided to help coordinate one-shot
        or triggered conversions. The Conversion Ready Flag bit is set after all
        conversions, averaging, and multiplications are complete. Conversion Ready Flag
        bit clears under the following conditions:
          1.) Writing to the Configuration Register (except for Power-Down selection)
          2.) Reading the Mask/Enable Register
        """
        return (self._read(REG_MASK_ENABLE) & self.__bitmask(CVRF)) >> CVRF

    @property
    def mathoverflow(self):
        """
        Math overflow flag read only method.
        This bit is set to '1' if an arithmetic operation resulted in an overflow error. It
        indicates that power data may have exceeded the maximum reportable value of
        419.43 W.
        """
        return (self._read(REG_MASK_ENABLE) & self.__bitmask(OVF)) >> OVF

    @property
    def configreg(self):
        """
        Content of configuration register. Read only property. If you
        want to change the contents use the dedicated register field
        properties
        """
        return self._read(REG_CONFIG)

    @property
    def mask_enablereg(self):
        """
        Content of mask/enable register. Read only property. If you
        want to change the contents use the dedicated register field
        properties
        """
        return self._read(REG_MASK_ENABLE)

    def __bitmask(self, bits): #pylint: disable=R0201
        """
        Returns bitmask for bits at positions <bits> where 0 denotes the LSB
        """
        if isinstance(bits, list):
            return sum(2**i for i in bits)
        else:
            return 2**bits

    def __setbits(self, reg, bits, value):
        """
        Sets bits at positions <bits> in <reg> to bit values given in <value>
        It is assumed that the LSB position is specified in index 0 of <bits>
        The resulting bit patterned is returned
        """

        reg &= ~self.__bitmask(bits) # Set all specified bits to zero
        reg |= value << bits[0] # Set specified bits to value <value>
        return reg

    def _read(self, reg):
        """
        Read a word from the device

        Parameters
        ---------
            reg: register address

        Returns
        ------
            list of bytes as characters for struct unpack

        """

        word = struct.unpack('>H', bytes(self.bus.read_i2c_block_data(self.address, reg, 2)))[0]
        return word

    def _write(self, reg, value):
        """
        Writes word <value> into register reg

        Parameters
        ----------
        reg : Byte
            Register address.
        value : Word
            Value to be written.

        Returns
        -------
        None.

        """

        #Convert value to little endian
        value = value & 0xFFFF
        #Exchange high-byte with low-byte
        value = struct.unpack('<H',struct.pack('>H', value))[0]

        self.bus.write_word_data(self.address, reg, value)

    def _set_bit(self, reg, bit, value=True):
        """

        Set bit at position <bit> (0..15) of the register <reg>

        Parameters
        ----------
        reg : TYPE
            Register address of which bit should be set
        bit : TYPE
            position of bit to be set. Can have value 0..15
        value : Boolean
            Default TRUE, if FALSE the bit is not set but cleared

        Returns
        -------
        None.

        """
        regval = self._read(reg)
        if value:
            regval |= 1 << bit
        else:
            regval &= ~(1 << bit)
        self._write(reg, regval)

    def voltage(self):
        """
        Returns the bus voltage in Volts

        """
        voltage = self._read(REG_BUS_VOLTAGE)
        voltage *= V_per_Bit / self.__fvdiv # 1.25mv/bit. Correction for voltage divider

        return voltage

    def current(self):
        """
        Returns the current in Amps

        """
        current = self._read(REG_CURRENT)

        # Fix 2's complement
        if current & (1 << 15):
            current -= 65535

        current *= A_per_Bit # 1.25mA/bit

        return current

    def power(self):
        """
        Returns the power calculated by the device in Watts

        This will probably be different to reading voltage and current
        and performing the calculation manually.
        """

        power = self._read(REG_POWER)
        power *= W_per_Bit / self.__fvdiv # 10mW/bit. Correction for voltage divider

        return power

    def manufacturer_id(self):
        """
        Returns the manufacturer ID - should always be 0x5449

        """
        man_id = self._read(REG_MANUFACTURER_ID)
        return man_id


    def die_id(self):
        """
        Returns the die ID - should be 0x227.
        """
        die_id = self._read(REG_DIE_ID)
        die_id = die_id >> 4
        return die_id

    def die_rev(self):
        """
        Returns the die revision - should be 0x0.
        """
        die_rev = self._read(REG_DIE_ID)
        die_rev = die_rev & 0x000F
        return die_rev

    def reset(self):
        """
        Generates a system reset that is the same as power-on reset.
        Resets all registers to default values.

        Returns
        -------
        None.

        """
        self._set_bit(REG_CONFIG, RST)

    def __del__(self):
        self.bus.close()
