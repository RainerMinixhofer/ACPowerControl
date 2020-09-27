#!/usr/bin/python3
# -*- coding: utf-8 -*-
#pylint: disable=C0103,C0301
"""
Test 1.5Inch OLED Display control via SSD1351 Controller

Created on Sat Aug 29 22:12:34 2020

@author: Rainer Minixhofer
"""

#--------------GPIO Library-----------------#
import RPi.GPIO as GPIO #pylint: disable=E0401
#--------------Image Library---------------#
from PIL  import Image  #pylint: disable=E0401
from PIL import ImageDraw  #pylint: disable=E0401
from PIL import ImageFont  #pylint: disable=E0401
#from PIL import ImageColor # pylint: disable=W0611
import pytest
#--------------Driver Library-----------------#
import OLEDDriver as OLED
#-------------Test Display Functions---------------#

@pytest.fixture(name='OLEDDisplay')
def fixture_OLEDDisplay():
    """
    Initializes 1.5Inch OLED Display control via SSD1351 Controller
    """
    OLED.Device_Init()
    yield OLED
    OLED.Clear_Screen()
#    GPIO.cleanup()

def test_OLEDDisplay_Pattern(OLEDDisplay):
    """
    Display Test Pattern
    """
    image = Image.new("RGB", (OLED.SSD1351_WIDTH, OLED.SSD1351_HEIGHT), "BLACK")
    draw = ImageDraw.Draw(image)

    draw.line([(0, 8), (127, 8)], fill="RED", width=16)
    draw.line([(0, 24), (127, 24)], fill="YELLOW", width=16)
    draw.line([(0, 40), (127, 40)], fill="GREEN", width=16)
    draw.line([(0, 56), (127, 56)], fill="CYAN", width=16)
    draw.line([(0, 72), (127, 72)], fill="BLUE", width=16)
    draw.line([(0, 88), (127, 88)], fill="MAGENTA", width=16)
    draw.line([(0, 104), (127, 104)], fill="BLACK", width=16)
    draw.line([(0, 120), (127, 120)], fill="WHITE", width=16)

    OLEDDisplay.Display_Image(image)
    OLEDDisplay.Delay(2000)

def test_OLEDDisplay_Text(OLEDDisplay):
    """
    Display Test Text
    """
    image = Image.new("RGB", (OLED.SSD1351_WIDTH, OLED.SSD1351_HEIGHT), "BLACK")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('cambriab.ttf', 24)

    draw.text((0, 12), 'WaveShare', fill="BLUE", font=font)
    draw.text((0, 36), 'Electronic', fill="BLUE", font=font)
    draw.text((20, 72), '1.5 inch', fill="CYAN", font=font)
    draw.text((10, 96), 'R', fill="RED", font=font)
    draw.text((25, 96), 'G', fill="GREEN", font=font)
    draw.text((40, 96), 'B', fill="BLUE", font=font)
    draw.text((55, 96), ' OLED', fill="CYAN", font=font)

    OLEDDisplay.Display_Image(image)
    OLEDDisplay.Delay(2000)

def test_OLEDDisplay_Lines(OLEDDisplay):
    """
    Display Test Lines
    """
    image = Image.new("RGB", (OLED.SSD1351_WIDTH, OLED.SSD1351_HEIGHT), "BLACK")
    draw = ImageDraw.Draw(image)

    for x in range(0, int((OLED.SSD1351_WIDTH-1)/2), 6):
        draw.line([(0, 0), (x, OLED.SSD1351_HEIGHT - 1)], fill="RED", width=1)
        draw.line([(0, 0), ((OLED.SSD1351_WIDTH-1) - x, OLED.SSD1351_HEIGHT - 1)], fill="RED", width=1)
        draw.line([(0, 0), (OLED.SSD1351_WIDTH - 1, x)], fill="RED", width=1)
        draw.line([(0, 0), (OLED.SSD1351_WIDTH - 1, (OLED.SSD1351_HEIGHT-1) - x)], fill="RED", width=1)
        OLEDDisplay.Display_Image(image)
    OLEDDisplay.Delay(250)
    draw.rectangle([0, 0, OLED.SSD1351_WIDTH - 1, OLED.SSD1351_HEIGHT - 1], fill="BLACK", outline="BLACK")

    for x in range(0, int((OLED.SSD1351_WIDTH-1)/2), 6):
        draw.line([(OLED.SSD1351_WIDTH - 1, 0), (x, OLED.SSD1351_HEIGHT - 1)], fill="YELLOW", width=1)
        draw.line([(OLED.SSD1351_WIDTH - 1, 0), (x + int((OLED.SSD1351_WIDTH-1)/2), OLED.SSD1351_HEIGHT - 1)], fill="YELLOW", width=1)
        draw.line([(OLED.SSD1351_WIDTH - 1, 0), (0, x)], fill="YELLOW", width=1)
        draw.line([(OLED.SSD1351_WIDTH - 1, 0), (0, x + int((OLED.SSD1351_HEIGHT-1)/2))], fill="YELLOW", width=1)
        OLEDDisplay.Display_Image(image)
    OLEDDisplay.Delay(250)
    draw.rectangle([0, 0, OLED.SSD1351_WIDTH - 1, OLED.SSD1351_HEIGHT - 1], fill="BLACK", outline="BLACK")

    for x in range(0, int((OLED.SSD1351_WIDTH-1)/2), 6):
        draw.line([(0, OLED.SSD1351_HEIGHT - 1), (x, 0)], fill="BLUE", width=1)
        draw.line([(0, OLED.SSD1351_HEIGHT - 1), (x + int((OLED.SSD1351_WIDTH-1)/2), 0)], fill="BLUE", width=1)
        draw.line([(0, OLED.SSD1351_HEIGHT - 1), (OLED.SSD1351_WIDTH - 1, x)], fill="BLUE", width=1)
        draw.line([(0, OLED.SSD1351_HEIGHT - 1), (OLED.SSD1351_WIDTH - 1, x + (OLED.SSD1351_HEIGHT-1)/2)], fill="BLUE", width=1)
        OLEDDisplay.Display_Image(image)
    draw.rectangle([0, 0, OLED.SSD1351_WIDTH - 1, OLED.SSD1351_HEIGHT - 1], fill="BLACK", outline="BLACK")
    OLEDDisplay.Delay(250)

    for x in range(0, int((OLED.SSD1351_WIDTH-1)/2), 6):
        draw.line([(OLED.SSD1351_WIDTH - 1, OLED.SSD1351_HEIGHT - 1), (x, 0)], fill="GREEN", width=1)
        draw.line([(OLED.SSD1351_WIDTH - 1, OLED.SSD1351_HEIGHT - 1), (x + int((OLED.SSD1351_WIDTH-1)/2), 0)], fill="GREEN", width=1)
        draw.line([(OLED.SSD1351_WIDTH - 1, OLED.SSD1351_HEIGHT - 1), (0, x)], fill="GREEN", width=1)
        draw.line([(OLED.SSD1351_WIDTH - 1, OLED.SSD1351_HEIGHT - 1), (0, x + int((OLED.SSD1351_HEIGHT-1)/2))], fill="GREEN", width=1)
        OLEDDisplay.Display_Image(image)
    draw.rectangle([0, 0, OLED.SSD1351_WIDTH - 1, OLED.SSD1351_HEIGHT - 1], fill="BLACK")
    OLEDDisplay.Delay(2000)

def test_OLEDDisplay_HV_Lines(OLEDDisplay):
    """
    Display Test HV Lines
    """
    image = Image.new("RGB", (OLED.SSD1351_WIDTH, OLED.SSD1351_HEIGHT), "BLACK")
    draw = ImageDraw.Draw(image)

    for y in range(0, OLED.SSD1351_HEIGHT - 1, 5):
        draw.line([(0, y), (OLED.SSD1351_WIDTH - 1, y)], fill="WHITE", width=1)
    OLEDDisplay.Display_Image(image)
    OLEDDisplay.Delay(250)
    for x in range(0, OLED.SSD1351_WIDTH - 1, 5):
        draw.line([(x, 0), (x, OLED.SSD1351_HEIGHT - 1)], fill="WHITE", width=1)
    OLEDDisplay.Display_Image(image)
    OLEDDisplay.Delay(2000)

def test_OLEDDisplay_Rects(OLEDDisplay):
    """
    Display Test Rectangles
    """
    image = Image.new("RGB", (OLED.SSD1351_WIDTH, OLED.SSD1351_HEIGHT), "BLACK")
    draw = ImageDraw.Draw(image)

    for x in range(0, int((OLED.SSD1351_WIDTH-1)/2), 6):
        draw.rectangle([(x, x), (OLED.SSD1351_WIDTH- 1 - x, OLED.SSD1351_HEIGHT-1 - x)], fill=None, outline="WHITE")
    OLEDDisplay.Display_Image(image)
    OLEDDisplay.Delay(2000)

def test_OLEDDisplay_FillRects(OLEDDisplay):
    """
    Display Filled Test Rectangles
    """
    image = Image.new("RGB", (OLED.SSD1351_WIDTH, OLED.SSD1351_HEIGHT), "BLACK")
    draw = ImageDraw.Draw(image)

    for x in range(OLED.SSD1351_HEIGHT-1, int((OLED.SSD1351_HEIGHT-1)/2), -6):
        draw.rectangle([(x, x), ((OLED.SSD1351_WIDTH-1) - x, (OLED.SSD1351_HEIGHT-1) - x)], fill="BLUE", outline="BLUE")
        draw.rectangle([(x, x), ((OLED.SSD1351_WIDTH-1) - x, (OLED.SSD1351_HEIGHT-1) - x)], fill=None, outline="YELLOW")
    OLEDDisplay.Display_Image(image)
    OLEDDisplay.Delay(2000)

def test_OLEDDisplay_Circles(OLEDDisplay):
    """
    Display Test Circles
    """
    image = Image.new("RGB", (OLED.SSD1351_WIDTH, OLED.SSD1351_HEIGHT), "BLACK")
    draw = ImageDraw.Draw(image)

    draw.ellipse([(0, 0), (OLED.SSD1351_WIDTH - 1, OLED.SSD1351_HEIGHT - 1)], fill="BLUE", outline="BLUE")
    OLEDDisplay.Display_Image(image)
    OLEDDisplay.Delay(500)
    for r in range(0, int(OLED.SSD1351_WIDTH/2) + 4, 4):
        draw.ellipse([(r, r), ((OLED.SSD1351_WIDTH-1) - r, (OLED.SSD1351_HEIGHT-1) - r)], fill=None, outline="YELLOW")
    OLEDDisplay.Display_Image(image)
    OLEDDisplay.Delay(2000)

def test_OLEDDisplay_Triangles(OLEDDisplay):
    """
    Display Test Triangles
    """
    image = Image.new("RGB", (OLED.SSD1351_WIDTH, OLED.SSD1351_HEIGHT), "BLACK")
    draw = ImageDraw.Draw(image)

    for i in range(0, int(OLED.SSD1351_WIDTH/2), 4):
        draw.line([(i, OLED.SSD1351_HEIGHT - 1 - i), (OLED.SSD1351_WIDTH/2, i)], fill=(255 - i*4, i*4, 255 - i*4), width=1)
        draw.line([(i, OLED.SSD1351_HEIGHT - 1 - i), (OLED.SSD1351_WIDTH - 1 - i, OLED.SSD1351_HEIGHT - 1 - i)], fill=(i*4, i*4, 255 - i*4), width=1)
        draw.line([(OLED.SSD1351_WIDTH - 1 - i, OLED.SSD1351_HEIGHT - 1 - i), (OLED.SSD1351_WIDTH/2, i)], fill=(i*4, 255 - i*4, i*4), width=1)
        OLEDDisplay.Display_Image(image)

    OLEDDisplay.Delay(2000)

def Display_Picture(OLEDDisplay, File_Name):
    """
    Display Test Picture from file <File_Name>
    """
    image = Image.open(File_Name)
    OLEDDisplay.Display_Image(image)

def test_OLEDDisplay_Picture1(OLEDDisplay):
    """
    Display Test Picture "picture1.jpg"
    """
    Display_Picture(OLEDDisplay,"picture1.jpg")
    OLEDDisplay.Delay(2000)

def test_OLEDDisplay_Picture2(OLEDDisplay):
    """
    Display Test Picture "picture2.jpg"
    """
    Display_Picture(OLEDDisplay,"picture2.jpg")
    OLEDDisplay.Delay(2000)

def test_OLEDDisplay_Picture3(OLEDDisplay):
    """
    Display Test Picture "picture3.jpg"
    """
    Display_Picture(OLEDDisplay,"picture3.jpg")
    OLEDDisplay.Delay(2000)
