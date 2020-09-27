#!/usr/bin/python3
# -*- coding:UTF-8 -*-
# pylint: disable=C0103,R0913,R0915
"""
OLED Display Driver Class Module
"""
import time

import RPi.GPIO as GPIO #pylint: disable=E0401

import spidev #pylint: disable=E0401

#pylint: disable=C0326
#SSD1351 Commands
SSD1351_WIDTH               = 128
SSD1351_HEIGHT              = 128
SSD1351_CMD_SETCOLUMN       = 0x15
SSD1351_CMD_SETROW          = 0x75
SSD1351_CMD_WRITERAM        = 0x5C
SSD1351_CMD_READRAM         = 0x5D
SSD1351_CMD_SETREMAP        = 0xA0
SSD1351_CMD_STARTLINE       = 0xA1
SSD1351_CMD_DISPLAYOFFSET   = 0xA2
#Four Display modes
SSD1351_CMD_DISPLAYALLOFF   = 0xA4
SSD1351_CMD_DISPLAYALLON    = 0xA5
SSD1351_CMD_NORMALDISPLAY   = 0xA6
SSD1351_CMD_INVERTDISPLAY   = 0xA7

SSD1351_CMD_FUNCTIONSELECT  = 0xAB
SSD1351_CMD_NOP1            = 0xAD
#Two sleep modes
SSD1351_CMD_DISPLAYOFF      = 0xAE
SSD1351_CMD_DISPLAYON       = 0xAF

SSD1351_CMD_NOP2            = 0xB0
SSD1351_CMD_PRECHARGE       = 0xB1
SSD1351_CMD_DISPLAYENHANCE  = 0xB2
SSD1351_CMD_CLOCKDIV        = 0xB3
SSD1351_CMD_SETVSL          = 0xB4
SSD1351_CMD_SETGPIO         = 0xB5
SSD1351_CMD_PRECHARGE2      = 0xB6
SSD1351_CMD_SETGRAY         = 0xB8
SSD1351_CMD_USELUT          = 0xB9
SSD1351_CMD_PRECHARGELEVEL  = 0xBB
SSD1351_CMD_VCOMH           = 0xBE
SSD1351_CMD_CONTRASTABC     = 0xC1
SSD1351_CMD_CONTRASTMASTER  = 0xC7
SSD1351_CMD_MUXRATIO        = 0xCA
SSD1351_CMD_NOP3            = 0xD1
SSD1351_CMD_NOP4            = 0xE3
SSD1351_CMD_COMMANDLOCK     = 0xFD
SSD1351_CMD_HORIZSCROLL     = 0x96
SSD1351_CMD_STOPSCROLL      = 0x9E
SSD1351_CMD_STARTSCROLL     = 0x9F

#color
BLACK   = 0x0000
BLUE    = 0x001F
RED     = 0xF800
GREEN   = 0x07E0
CYAN    = 0x07FF
MAGENTA = 0xF81F
YELLOW  = 0xFFE0
WHITE   = 0xFFFF
#pylint: enable=C0326

class OLEDDriver:
    """
    Driver Class for 1.5\" OLED Display with SSD1351 MCU Controller
    """

    def __init__(self, SPIBus=0, SPIDev=0, RSTPin=25, DCPin=24, CSPin=8):
        """
        Initialize Display
        """
        #GPIO Set
        GPIO.setmode(GPIO.BCM)
        self.RST_PIN = RSTPin #RST: Reset pin. Pull low for reset for at least 2us
        self.DC_PIN = DCPin #D/C Pin: Low for command, high for data
        self.CS_PIN = CSPin #CS: Chip Select Pin. Low to enable device, high to disable
        #buffers
        self.__color_byte = [0x00, 0x00]
        self.__color_fill_byte = [0x00, 0x00]*(SSD1351_WIDTH)
        #GPIO init
        GPIO.setwarnings(False)
        GPIO.setup(self.RST_PIN, GPIO.OUT)
        GPIO.setup(self.DC_PIN, GPIO.OUT)
        GPIO.setup(self.CS_PIN, GPIO.OUT)
        #SPI init
        self.SPI = spidev.SpiDev(SPIBus, SPIDev)
        self.SPI.max_speed_hz = 9000000 # 9MHz SPI Clock Frequency
        self.SPI.mode = 0b00 #SPI Mode 0: Clock idle at low, Clock Phase at first edge
        #Initialize commands of SSD1351 Controller
        #CS to low enables device
        self.OLED_CS(0)
        #RST to low resets device, release reset after 100ms
        self.OLED_RST(0)
        time.sleep(0.1)
        self.OLED_RST(1)
        #wait 500ms to let device runs its initialization
        time.sleep(0.5)

        #Command Lock Settings to enable commands and extended command-set
        self.Write_Command(SSD1351_CMD_COMMANDLOCK)
        #  Unlock OLED driver IC MCU interface from entering command
        self.Write_Data(0x12)
        #Command Lock Settings
        self.Write_Command(SSD1351_CMD_COMMANDLOCK)	# command lock
        #  Command 0xA2,0xB1,0xB3,0xBB,0xBE,0xC1 accessible if in unlock state
        self.Write_Data(0xB1)
        #Switch Display off
        #  The segment is in VSS state and common is in high impedance state.
        self.Write_Command(SSD1351_CMD_DISPLAYOFF)
        #Display mode Entire Display OFF
        #  Force the entire display to be at gray scale level “GS0” regardless of the
        #  contents of the display data RAM.
        self.Write_Command(SSD1351_CMD_DISPLAYALLOFF)
        #Set column address range to default values
        self.Write_Command(SSD1351_CMD_SETCOLUMN)
        #  column address start 0
        self.Write_Data(0x00)
        #  column address end 127
        self.Write_Data(0x7f)
        #Set row address range to default values
        self.Write_Command(SSD1351_CMD_SETROW)
        #  row address start 0
        self.Write_Data(0x00)
        #  row address end 127
        self.Write_Data(0x7f)
        #Set Front Clock Divider / Oscillator Frequency
        self.Write_Command(SSD1351_CMD_CLOCKDIV)
        #  Front Clock Divide Ratio
        #    A[3:0]:0b0001 Set the divide ratio to generate DCLK (Display Clock) from CLK to one
        #    A[7:4]:0b1111 Oscillator Frequency. Is Fosc=2.8MHz(typ) for A[7:4]=0b1101, and thus
        #      this setting yields 2.8*15/13=3.23MHz
        self.Write_Data(0xF1)
        #Set MUX Ratio
        self.Write_Command(SSD1351_CMD_MUXRATIO)
        #  128MUX (default)
        self.Write_Data(0x7F)
        #Set Re-map/Color Depth (Display RAM to Panel)
        self.Write_Command(SSD1351_CMD_SETREMAP)	# set re-map & data format
        #  A[0]:0b0 Horizontal address increment (default)
        #  A[1]:0b0 Column address is mapped to SEG0 (default)
        #  A[2]:0b1 Color sequence is swapped: C->B->A
        #  A[3]:0b0 Reserved
        #  A[4]:0b1 Scan from COM0 to COM[N-1] (default)
        #  A[5]:0b1 Enable COM Split Odd Even (default)
        #  A[7:6]:0b01 65k Color Depth (default)
        self.Write_Data(0x74)    # Horizontal address increment
        #set display start line
        self.Write_Command(SSD1351_CMD_STARTLINE)
        #  start 00 line
        self.Write_Data(0x00)
        #set display offset
        self.Write_Command(SSD1351_CMD_DISPLAYOFFSET)
        #  Set vertical scroll by Row to 00
        self.Write_Data(0x00)
        #Function Selection
        self.Write_Command(SSD1351_CMD_FUNCTIONSELECT)
        #  A[0]=0b1: Enable internal Vdd regulator
        #  A[7:6]=0b00, Select 8-bit SPI interface
        self.Write_Data(0x01)
        #Set Segment Low Voltage
        self.Write_Command(SSD1351_CMD_SETVSL)
        #  A[1:0]=0b00 External VSL [reset default]
        self.Write_Data(0xA0) # 0b101000<A1><A0>
        self.Write_Data(0xB5) # 0b10110101 (fixed)
        self.Write_Data(0x55) # 0b01010101 (fixed)
        #Set Contrast Current for Color A,B,C
        self.Write_Command(SSD1351_CMD_CONTRASTABC)
        #  Contrast value color A 0b11001000
        self.Write_Data(0xC8)
        #  Contrast value color B 0b10000000
        self.Write_Data(0x80)
        #  Contrast value color C 0b11000000
        self.Write_Data(0xC0)
        #Master Contrast Current Control
        self.Write_Command(SSD1351_CMD_CONTRASTMASTER)
        #  A[3:0]=0b1111: No change [reset default]
        self.Write_Data(0x0F)
        #Set Reset(Phase 1) / Pre-charge (Phase 2) period
        self.Write_Command(SSD1351_CMD_PRECHARGE)
        #  A[3:0]=0b0010: Phase 1 period of 7 DCLKs
        #  A[7:4]=0b0011: Phase 2 period of 3 DCLKs
        self.Write_Data(0x32)
        #Display Enhancement
        self.Write_Command(SSD1351_CMD_DISPLAYENHANCE)
        #  A[7:0]=0b10100100 Enhance Display Performance
        self.Write_Data(0xA4) #0x00 for normal (default) 0xA4 for enhanced display performance
        self.Write_Data(0x00) #0b00000000 (fixed)
        self.Write_Data(0x00) #0b00000000 (fixed)
        #Set Pre-charge voltage to 0.5xVcc
        self.Write_Command(SSD1351_CMD_PRECHARGELEVEL)
        #  A[4:0]=0b00000 means 0.2xVcc, A[4:0]=0b11111 means 0.6xVcc
        #  Thus the Vcc multiplier calculates as 0.2+0.4/31*A[4:0]
        #  Which is 0.497xVcc~0.5xVcc
        self.Write_Data(0x17)
        #Set second Pre-charge Period to 1 DCLKS
        self.Write_Command(SSD1351_CMD_PRECHARGE2)
        #  A[3:0]=0b0001 is 1 DCLKS, A[3:0]=0b1000 is 8 DCLKS (default)
        self.Write_Data(0x01)
        #Set Vcomh voltage
        self.Write_Command(SSD1351_CMD_VCOMH)
        #  A[2:0]=0b101 sets Vcomh voltage to default 0.82xVcc
        self.Write_Data(0x05)
        #Set Display Mode to default Normal Mode
        self.Write_Command(SSD1351_CMD_NORMALDISPLAY)

        self.Clear_Screen()
        #Switch Sleep Mode off and thus display on
        self.Write_Command(SSD1351_CMD_DISPLAYON)

    @property
    def w(self):
        return SSD1351_WIDTH
    
    @property
    def h(self):
        return SSD1351_HEIGHT

    def Set_Color(self, color):
        """
        Set Color Bytewise
        """
        self.__color_byte[0] = (color >> 8) & 0xff
        self.__color_byte[1] = color & 0xff

    def OLED_RST(self, x):
        """
        Set OLED RST Pin to level x (x==0 for low and x!=0 for high)
        """
        GPIO.output(self.RST_PIN, GPIO.LOW if x == 0 else GPIO.HIGH)

    def OLED_DC(self, x):
        """
        Set OLED DC Pin to level x (x==0 for low and x!=0 for high)
        """
        GPIO.output(self.DC_PIN, GPIO.LOW if x == 0 else GPIO.HIGH)

    def OLED_CS(self, x):
        """
        Set OLED CS Pin to level x (x==0 for low and x!=0 for high)
        """
        GPIO.output(self.CS_PIN, GPIO.LOW if x == 0 else GPIO.HIGH)

    def SPI_WriteByte(self, byte):
        """
        Write byte <byte> to SPI bus
        """
        self.SPI.writebytes(byte)

    def Write_Command(self, cmd):
        """
        Write command <cmd> to OLED display
        """
        self.OLED_CS(0)
        self.OLED_DC(0)
        self.SPI_WriteByte([cmd])
        self.OLED_CS(1)

    def Write_Data(self, dat):
        """
        Write data <dat> to OLED display
        """
        self.OLED_CS(0)
        self.OLED_DC(1)
        self.SPI_WriteByte([dat])
        self.OLED_CS(1)

    def Write_Datas(self, data):
        """
        Write data array in <data> to OLED display
        """
        self.OLED_CS(0)
        self.OLED_DC(1)
        self.SPI_WriteByte(data)
        self.OLED_CS(1)

    def RAM_Address(self):
        """
        Reset row and column start and end addresses to the maximum range [0,127]
        and [0,127] respectively
        """
        self.Write_Command(SSD1351_CMD_SETCOLUMN)
        self.Write_Data(0x00)
        self.Write_Data(0x7f)
        self.Write_Command(SSD1351_CMD_SETROW)
        self.Write_Data(0x00)
        self.Write_Data(0x7f)

    def Fill_Color(self, color):
        """
        Fill OLED display with color <color>
        """

        self.RAM_Address() # Reset row and column address ranges
        self.Write_Command(SSD1351_CMD_WRITERAM) # Enable MCU to write Data into RAM
        self.Set_Color(color) # Write into global color_byte buffer variable
        # shift color_byte buffer by 7 bits and write into color_fill_Byte
        self.__color_fill_byte = self.__color_byte*SSD1351_WIDTH
        self.OLED_CS(0)
        self.OLED_DC(1)
        for _ in range(0, SSD1351_HEIGHT):
            self.SPI_WriteByte(self.__color_fill_byte)
        self.OLED_CS(1)

    def Clear_Screen(self):
        """
        Clear OLED Display
        """

        self.RAM_Address()
        self.Write_Command(SSD1351_CMD_WRITERAM)
        self.__color_fill_byte = [0x00, 0x00] *SSD1351_WIDTH
        self.OLED_CS(0)
        self.OLED_DC(1)
        for _ in range(0, SSD1351_HEIGHT):
            self.SPI_WriteByte(self.__color_fill_byte)
        self.OLED_CS(1)

    def Draw_Pixel(self, x, y):
        """
        Set pixel color at x, y position to color <color_byte>
        """
        # Bounds check.
        if ((x >= SSD1351_WIDTH) or (y >= SSD1351_HEIGHT)):
            return
        if ((x < 0) or (y < 0)):
            return
        self.Set_Address(x, y)
        # transfer data
        self.Write_Datas(self.__color_byte)

    def Set_Coordinate(self, x, y):
        """
        Set pixel coordinates to x, y
        """
        if((x >= SSD1351_WIDTH) or (y >= SSD1351_HEIGHT)):
            return
        # Set x and y coordinate
        self.Write_Command(SSD1351_CMD_SETCOLUMN)
        self.Write_Data(x)
        self.Write_Data(SSD1351_WIDTH-1)
        self.Write_Command(SSD1351_CMD_SETROW)
        self.Write_Data(y)
        self.Write_Data(SSD1351_HEIGHT-1)
        self.Write_Command(SSD1351_CMD_WRITERAM)

    def Set_Address(self, column, row):
        """
        Set RAM column to column and start row to row and stop row to row+7
        """
        self.Write_Command(SSD1351_CMD_SETCOLUMN)
        self.Write_Data(column)  #X start
        self.Write_Data(column)  #X end
        self.Write_Command(SSD1351_CMD_SETROW)
        self.Write_Data(row)     #Y start
        self.Write_Data(row+7)   #Y end
        self.Write_Command(SSD1351_CMD_WRITERAM)

    def Write_text(self, dat):
        """
        Write text <dat> on display
        """
        for _ in range(0, 8):
            if dat & 0x01:
                self.Write_Datas(self.__color_byte)
            else:
                self.Write_Datas([0x00, 0x00])
            dat = dat >> 1

    def Invert(self, v):
        """
        Invert whole display if <v> is True
        """
        self.Write_Command(SSD1351_CMD_INVERTDISPLAY if v else SSD1351_CMD_NORMALDISPLAY)

    def Draw_FastHLine(self, x, y, length):
        """
        Draw a horizontal line ignoring any screen rotation.
        """
        # Bounds check
        if((x >= SSD1351_WIDTH) or (y >= SSD1351_HEIGHT)):
            return
        # X bounds check
        if (x+length) > SSD1351_WIDTH:
            length = SSD1351_WIDTH - x - 1
        if length < 0:
            return
        # set location
        self.Write_Command(SSD1351_CMD_SETCOLUMN)
        self.Write_Data(x)
        self.Write_Data(x+length-1)
        self.Write_Command(SSD1351_CMD_SETROW)
        self.Write_Data(y)
        self.Write_Data(y)
        # fill!
        self.Write_Command(SSD1351_CMD_WRITERAM)

        for _ in range(0, length):
            self.Write_Datas(self.__color_byte)

    def Draw_FastVLine(self, x, y, length):
        """
        Draw a vertical line ignoring any screen rotation.
        """
        # Bounds check
        if((x >= SSD1351_WIDTH) or (y >= SSD1351_HEIGHT)):
            return
        # X bounds check
        if y+length > SSD1351_HEIGHT:
            length = SSD1351_HEIGHT - y - 1
        if length < 0:
            return
        # set location
        self.Write_Command(SSD1351_CMD_SETCOLUMN)
        self.Write_Data(x)
        self.Write_Data(x)
        self.Write_Command(SSD1351_CMD_SETROW)
        self.Write_Data(y)
        self.Write_Data(y+length-1)
        # fill!
        self.Write_Command(SSD1351_CMD_WRITERAM)

        for _ in range(0, length):
            self.Write_Datas(self.__color_byte)

    def Display_Image(self, Image):
        """
        Display an image given in PIL object <Image>
        """
        if Image is None:
            return

        self.Set_Coordinate(0, 0)
        buffer1 = Image.load()
        for j in range(0, SSD1351_WIDTH):
            for i in range(0, SSD1351_HEIGHT):
                self.__color_fill_byte[i*2] = ((buffer1[i, j][0] & 0xF8)|\
                                               (buffer1[i, j][1] >> 5))
                self.__color_fill_byte[i*2+1] = (((buffer1[i, j][1] << 3) & 0xE0)|\
                                                  (buffer1[i, j][2] >> 3))
            self.Write_Datas(self.__color_fill_byte)

    def __del__(self):
        self.Clear_Screen()
        GPIO.cleanup()
        self.SPI.close()
