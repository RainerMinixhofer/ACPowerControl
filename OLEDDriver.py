#!/usr/bin/python3
# -*- coding:UTF-8 -*-
# pylint: disable=C0103
"""
OLED Display Driver Module
"""
import time

import RPi.GPIO as GPIO #pylint: disable=E0401

import spidev #pylint: disable=E0401

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

#buffer
color_byte = [0x00, 0x00]
color_fill_byte = [0x00, 0x00]*(SSD1351_WIDTH)


#GPIO Set
GPIO.setmode(GPIO.BCM)
OLED_RST_PIN = 25 #RST: Reset pin. Pull low for reset for at least 2us
OLED_DC_PIN = 24 #D/C Pin: Low for command, high for data
OLED_CS_PIN = 8 #CS: Chip Select Pin. Low to enable device, high to disable
#GPIO init
GPIO.setwarnings(False)
GPIO.setup(OLED_RST_PIN, GPIO.OUT)
GPIO.setup(OLED_DC_PIN, GPIO.OUT)
GPIO.setup(OLED_CS_PIN, GPIO.OUT)
#SPI init
SPI = spidev.SpiDev(0, 0)
SPI.max_speed_hz = 9000000 # 9MHz SPI Clock Frequency
SPI.mode = 0b00 #SPI Mode 0: Clock idle at low, Clock Phase at first edge


def Set_Color(color):
    """
    Set Color Bytewise
    """
    color_byte[0] = (color >> 8) & 0xff
    color_byte[1] = color & 0xff

def OLED_RST(x):
    """
    Set OLED RST Pin to level x (x==0 for low and x!=0 for high)
    """
    GPIO.output(OLED_RST_PIN, GPIO.LOW if x == 0 else GPIO.HIGH)

def OLED_DC(x):
    """
    Set OLED DC Pin to level x (x==0 for low and x!=0 for high)
    """
    GPIO.output(OLED_DC_PIN, GPIO.LOW if x == 0 else GPIO.HIGH)

def OLED_CS(x):
    """
    Set OLED CS Pin to level x (x==0 for low and x!=0 for high)
    """
    GPIO.output(OLED_CS_PIN, GPIO.LOW if x == 0 else GPIO.HIGH)

def SPI_WriteByte(byte):
    """
    Write byte <byte> to SPI bus
    """
    SPI.writebytes(byte)

def Write_Command(cmd):
    """
    Write command <cmd> to OLED display
    """
    OLED_CS(0)
    OLED_DC(0)
    SPI_WriteByte([cmd])
    OLED_CS(1)

def Write_Data(dat):
    """
    Write data <dat> to OLED display
    """
    OLED_CS(0)
    OLED_DC(1)
    SPI_WriteByte([dat])
    OLED_CS(1)

def Write_Datas(data):
    """
    Write data array in <data> to OLED display
    """
    OLED_CS(0)
    OLED_DC(1)
    SPI_WriteByte(data)
    OLED_CS(1)

def RAM_Address():
    """
    Reset row and column start and end addresses to the maximum range [0,127]
    and [0,127] respectively
    """
    Write_Command(SSD1351_CMD_SETCOLUMN)
    Write_Data(0x00)
    Write_Data(0x7f)
    Write_Command(SSD1351_CMD_SETROW)
    Write_Data(0x00)
    Write_Data(0x7f)

def Fill_Color(color):
    """
    Fill OLED display with color <color>
    """
    global color_fill_byte

    RAM_Address() # Reset row and column address ranges
    Write_Command(SSD1351_CMD_WRITERAM) # Enable MCU to write Data into RAM
    Set_Color(color) # Write into global color_byte buffer variable
    # shift color_byte buffer by 7 bits and write into color_fill_Byte
    color_fill_byte = color_byte*SSD1351_WIDTH
    OLED_CS(0)
    OLED_DC(1)
    for _ in range(0, SSD1351_HEIGHT):
        SPI_WriteByte(color_fill_byte)
    OLED_CS(1)

def Clear_Screen():
    """
    Clear OLED Display
    """
    global color_fill_byte

    RAM_Address()
    Write_Command(SSD1351_CMD_WRITERAM)
    color_fill_byte = [0x00, 0x00] *SSD1351_WIDTH
    OLED_CS(0)
    OLED_DC(1)
    for _ in range(0, SSD1351_HEIGHT):
        SPI_WriteByte(color_fill_byte)
    OLED_CS(1)

def Draw_Pixel(x, y):
    """
    Set pixel color at x, y position to color <color_byte>
    """
    # Bounds check.
    if ((x >= SSD1351_WIDTH) or (y >= SSD1351_HEIGHT)):
        return
    if ((x < 0) or (y < 0)):
        return
    Set_Address(x, y)
    # transfer data
    Write_Datas(color_byte)

def Set_Coordinate(x, y):
    """
    Set pixel coordinates to x, y
    """
    if((x >= SSD1351_WIDTH) or (y >= SSD1351_HEIGHT)):
        return
    # Set x and y coordinate
    Write_Command(SSD1351_CMD_SETCOLUMN)
    Write_Data(x)
    Write_Data(SSD1351_WIDTH-1)
    Write_Command(SSD1351_CMD_SETROW)
    Write_Data(y)
    Write_Data(SSD1351_HEIGHT-1)
    Write_Command(SSD1351_CMD_WRITERAM)


def Set_Address(column, row):
    """
    Set RAM column to column and start row to row and stop row to row+7
    """
    Write_Command(SSD1351_CMD_SETCOLUMN)
    Write_Data(column)  #X start
    Write_Data(column)  #X end
    Write_Command(SSD1351_CMD_SETROW)
    Write_Data(row)     #Y start
    Write_Data(row+7)   #Y end
    Write_Command(SSD1351_CMD_WRITERAM)

def Write_text(dat):
    """
    Write text <dat> on display
    """
    for _ in range(0, 8):
        if dat & 0x01:
            Write_Datas(color_byte)
        else:
            Write_Datas([0x00, 0x00])
        dat = dat >> 1

def Invert(v):
    """
    Invert whole display if <v> is True
    """
    Write_Command(SSD1351_CMD_INVERTDISPLAY if v else SSD1351_CMD_NORMALDISPLAY)

def Delay(x):
    """
    Wait for x Milliseconds
    """
    time.sleep(x / 1000.0)

def Device_Init():
    """
    Initialize Display
    """
    #CS to low enables device
    OLED_CS(0)
    #RST to low resets device, release reset after 500ms
    OLED_RST(0)
    Delay(500)
    OLED_RST(1)
    #wait 500ms to let device runs its initialization
    Delay(500)

    #Command Lock Settings to enable commands and extended command-set
    Write_Command(SSD1351_CMD_COMMANDLOCK)
    #  Unlock OLED driver IC MCU interface from entering command
    Write_Data(0x12)
    #Command Lock Settings
    Write_Command(SSD1351_CMD_COMMANDLOCK)	# command lock
    #  Command 0xA2,0xB1,0xB3,0xBB,0xBE,0xC1 accessible if in unlock state
    Write_Data(0xB1)
    #Switch Display off
    #  The segment is in VSS state and common is in high impedance state.
    Write_Command(SSD1351_CMD_DISPLAYOFF)
    #Display mode Entire Display OFF
    #  Force the entire display to be at gray scale level “GS0” regardless of the
    #  contents of the display data RAM.
    Write_Command(SSD1351_CMD_DISPLAYALLOFF)
    #Set column address range to default values
    Write_Command(SSD1351_CMD_SETCOLUMN)
    #  column address start 0
    Write_Data(0x00)
    #  column address end 127
    Write_Data(0x7f)
    #Set row address range to default values
    Write_Command(SSD1351_CMD_SETROW)
    #  row address start 0
    Write_Data(0x00)
    #  row address end 127
    Write_Data(0x7f)
    #Set Front Clock Divider / Oscillator Frequency
    Write_Command(SSD1351_CMD_CLOCKDIV)
    #  Front Clock Divide Ratio
    #    A[3:0]:0b0001 Set the divide ratio to generate DCLK (Display Clock) from CLK to one
    #    A[7:4]:0b1111 Oscillator Frequency. Is Fosc=2.8MHz(typ) for A[7:4]=0b1101, and thus
    #      this setting yields 2.8*15/13=3.23MHz
    Write_Data(0xF1)
    #Set MUX Ratio
    Write_Command(SSD1351_CMD_MUXRATIO)
    #  128MUX (default)
    Write_Data(0x7F)
    #Set Re-map/Color Depth (Display RAM to Panel)
    Write_Command(SSD1351_CMD_SETREMAP)	# set re-map & data format
    #  A[0]:0b0 Horizontal address increment (default)
    #  A[1]:0b0 Column address is mapped to SEG0 (default)
    #  A[2]:0b1 Color sequence is swapped: C->B->A
    #  A[3]:0b0 Reserved
    #  A[4]:0b1 Scan from COM0 to COM[N-1] (default)
    #  A[5]:0b1 Enable COM Split Odd Even (default)
    #  A[7:6]:0b01 65k Color Depth (default)
    Write_Data(0x74)    # Horizontal address increment
    #set display start line
    Write_Command(SSD1351_CMD_STARTLINE)
    #  start 00 line
    Write_Data(0x00)
    #set display offset
    Write_Command(SSD1351_CMD_DISPLAYOFFSET)
    #  Set vertical scroll by Row to 00
    Write_Data(0x00)
    #Function Selection
    Write_Command(SSD1351_CMD_FUNCTIONSELECT)
    #  A[0]=0b1: Enable internal Vdd regulator
    #  A[7:6]=0b00, Select 8-bit SPI interface
#    Write_Command(0x01)
    Write_Data(0x01)
    #Set Segment Low Voltage
    Write_Command(SSD1351_CMD_SETVSL)
    #  A[1:0]=0b00 External VSL [reset default]
    Write_Data(0xA0) # 0b101000<A1><A0>
    Write_Data(0xB5) # 0b10110101 (fixed)
    Write_Data(0x55) # 0b01010101 (fixed)
    #Set Contrast Current for Color A,B,C
    Write_Command(SSD1351_CMD_CONTRASTABC)
    #  Contrast value color A 0b11001000
    Write_Data(0xC8)
    #  Contrast value color B 0b10000000
    Write_Data(0x80)
    #  Contrast value color C 0b11000000
    Write_Data(0xC0)
    #Master Contrast Current Control
    Write_Command(SSD1351_CMD_CONTRASTMASTER)
    #  A[3:0]=0b1111: No change [reset default]
    Write_Data(0x0F)
    #Set Reset(Phase 1) / Pre-charge (Phase 2) period
    Write_Command(SSD1351_CMD_PRECHARGE)
    #  A[3:0]=0b0010: Phase 1 period of 7 DCLKs
    #  A[7:4]=0b0011: Phase 2 period of 3 DCLKs
    Write_Data(0x32)
    #Display Enhancement
    Write_Command(SSD1351_CMD_DISPLAYENHANCE)
    #  A[7:0]=0b10100100 Enhance Display Performance
    Write_Data(0xA4) #0x00 for normal (default) 0xA4 for enhanced display performance
    Write_Data(0x00) #0b00000000 (fixed)
    Write_Data(0x00) #0b00000000 (fixed)
    #Set Pre-charge voltage to 0.5xVcc
    Write_Command(SSD1351_CMD_PRECHARGELEVEL)
    #  A[4:0]=0b00000 means 0.2xVcc, A[4:0]=0b11111 means 0.6xVcc
    #  Thus the Vcc multiplier calculates as 0.2+0.4/31*A[4:0]
    #  Which is 0.497xVcc~0.5xVcc
    Write_Data(0x17)
    #Set second Pre-charge Period to 1 DCLKS
    Write_Command(SSD1351_CMD_PRECHARGE2)
    #  A[3:0]=0b0001 is 1 DCLKS, A[3:0]=0b1000 is 8 DCLKS (default)
    Write_Data(0x01)
    #Set Vcomh voltage
    Write_Command(SSD1351_CMD_VCOMH)
    #  A[2:0]=0b101 sets Vcomh voltage to default 0.82xVcc
    Write_Data(0x05)
    #Set Display Mode to default Normal Mode
    Write_Command(SSD1351_CMD_NORMALDISPLAY)

    Clear_Screen()
    #Switch Sleep Mode off and thus display on
    Write_Command(SSD1351_CMD_DISPLAYON)


def Draw_FastHLine(x, y, length):
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
    Write_Command(SSD1351_CMD_SETCOLUMN)
    Write_Data(x)
    Write_Data(x+length-1)
    Write_Command(SSD1351_CMD_SETROW)
    Write_Data(y)
    Write_Data(y)
    # fill!
    Write_Command(SSD1351_CMD_WRITERAM)

    for _ in range(0, length):
        Write_Datas(color_byte)


def Draw_FastVLine(x, y, length):
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
    Write_Command(SSD1351_CMD_SETCOLUMN)
    Write_Data(x)
    Write_Data(x)
    Write_Command(SSD1351_CMD_SETROW)
    Write_Data(y)
    Write_Data(y+length-1)
    # fill!
    Write_Command(SSD1351_CMD_WRITERAM)

    for _ in range(0, length):
        Write_Datas(color_byte)

def Display_Image(Image):
    """
    Display an image given in PIL object <Image>
    """
    if Image is None:
        return

    Set_Coordinate(0, 0)
    buffer1 = Image.load()
    for j in range(0, SSD1351_WIDTH):
        for i in range(0, SSD1351_HEIGHT):
            color_fill_byte[i*2] = ((buffer1[i, j][0] & 0xF8)|(buffer1[i, j][1] >> 5))
            color_fill_byte[i*2+1] = (((buffer1[i, j][1] << 3) & 0xE0)|(buffer1[i, j][2] >> 3))
        Write_Datas(color_fill_byte)
