#!/usr/bin/python3
# -*- coding: utf-8 -*-
#pylint: disable=C0103,C0301
"""
Test 1.5Inch OLED Display control via SSD1351 Controller

Created on Sat Aug 29 22:12:34 2020

@author: Rainer Minixhofer
"""

import time
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
    oled = OLED.OLEDDriver()
    yield oled
    del oled

def test_OLEDDisplay_Pattern(OLEDDisplay):
    """
    Display Test Pattern
    """
    image = Image.new("RGB", (OLEDDisplay.w, OLEDDisplay.h), "BLACK")
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
    time.sleep(2.0)

def test_OLEDDisplay_Text(OLEDDisplay):
    """
    Display Test Text
    """
    image = Image.new("RGB", (OLEDDisplay.w, OLEDDisplay.h), "BLACK")
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
    time.sleep(2.0)

def test_OLEDDisplay_Lines(OLEDDisplay):
    """
    Display Test Lines
    """
    image = Image.new("RGB", (OLEDDisplay.w, OLEDDisplay.h), "BLACK")
    draw = ImageDraw.Draw(image)

    for x in range(0, int((OLEDDisplay.w-1)/2), 6):
        draw.line([(0, 0), (x, OLEDDisplay.h - 1)], fill="RED", width=1)
        draw.line([(0, 0), ((OLEDDisplay.w-1) - x, OLEDDisplay.h - 1)], fill="RED", width=1)
        draw.line([(0, 0), (OLEDDisplay.w - 1, x)], fill="RED", width=1)
        draw.line([(0, 0), (OLEDDisplay.w - 1, (OLEDDisplay.h-1) - x)], fill="RED", width=1)
        OLEDDisplay.Display_Image(image)
    time.sleep(0.25)
    draw.rectangle([0, 0, OLEDDisplay.w - 1, OLEDDisplay.h - 1], fill="BLACK", outline="BLACK")

    for x in range(0, int((OLEDDisplay.w-1)/2), 6):
        draw.line([(OLEDDisplay.w - 1, 0), (x, OLEDDisplay.h - 1)], fill="YELLOW", width=1)
        draw.line([(OLEDDisplay.w - 1, 0), (x + int((OLEDDisplay.w-1)/2), OLEDDisplay.h - 1)], fill="YELLOW", width=1)
        draw.line([(OLEDDisplay.w - 1, 0), (0, x)], fill="YELLOW", width=1)
        draw.line([(OLEDDisplay.w - 1, 0), (0, x + int((OLEDDisplay.h-1)/2))], fill="YELLOW", width=1)
        OLEDDisplay.Display_Image(image)
    time.sleep(0.25)
    draw.rectangle([0, 0, OLEDDisplay.w - 1, OLEDDisplay.h - 1], fill="BLACK", outline="BLACK")

    for x in range(0, int((OLEDDisplay.w-1)/2), 6):
        draw.line([(0, OLEDDisplay.h - 1), (x, 0)], fill="BLUE", width=1)
        draw.line([(0, OLEDDisplay.h - 1), (x + int((OLEDDisplay.w-1)/2), 0)], fill="BLUE", width=1)
        draw.line([(0, OLEDDisplay.h - 1), (OLEDDisplay.w - 1, x)], fill="BLUE", width=1)
        draw.line([(0, OLEDDisplay.h - 1), (OLEDDisplay.w - 1, x + (OLEDDisplay.h-1)/2)], fill="BLUE", width=1)
        OLEDDisplay.Display_Image(image)
    draw.rectangle([0, 0, OLEDDisplay.w - 1, OLEDDisplay.h - 1], fill="BLACK", outline="BLACK")
    time.sleep(0.25)

    for x in range(0, int((OLEDDisplay.w-1)/2), 6):
        draw.line([(OLEDDisplay.w - 1, OLEDDisplay.h - 1), (x, 0)], fill="GREEN", width=1)
        draw.line([(OLEDDisplay.w - 1, OLEDDisplay.h - 1), (x + int((OLEDDisplay.w-1)/2), 0)], fill="GREEN", width=1)
        draw.line([(OLEDDisplay.w - 1, OLEDDisplay.h - 1), (0, x)], fill="GREEN", width=1)
        draw.line([(OLEDDisplay.w - 1, OLEDDisplay.h - 1), (0, x + int((OLEDDisplay.h-1)/2))], fill="GREEN", width=1)
        OLEDDisplay.Display_Image(image)
    draw.rectangle([0, 0, OLEDDisplay.w - 1, OLEDDisplay.h - 1], fill="BLACK")
    time.sleep(2.0)

def test_OLEDDisplay_HV_Lines(OLEDDisplay):
    """
    Display Test HV Lines
    """
    image = Image.new("RGB", (OLEDDisplay.w, OLEDDisplay.h), "BLACK")
    draw = ImageDraw.Draw(image)

    for y in range(0, OLEDDisplay.h - 1, 5):
        draw.line([(0, y), (OLEDDisplay.w - 1, y)], fill="WHITE", width=1)
    OLEDDisplay.Display_Image(image)
    time.sleep(0.25)
    for x in range(0, OLEDDisplay.w - 1, 5):
        draw.line([(x, 0), (x, OLEDDisplay.h - 1)], fill="WHITE", width=1)
    OLEDDisplay.Display_Image(image)
    time.sleep(2.0)

def test_OLEDDisplay_Rects(OLEDDisplay):
    """
    Display Test Rectangles
    """
    image = Image.new("RGB", (OLEDDisplay.w, OLEDDisplay.h), "BLACK")
    draw = ImageDraw.Draw(image)

    for x in range(0, int((OLEDDisplay.w-1)/2), 6):
        draw.rectangle([(x, x), (OLEDDisplay.w- 1 - x, OLEDDisplay.h-1 - x)], fill=None, outline="WHITE")
    OLEDDisplay.Display_Image(image)
    time.sleep(2.0)

def test_OLEDDisplay_FillRects(OLEDDisplay):
    """
    Display Filled Test Rectangles
    """
    image = Image.new("RGB", (OLEDDisplay.w, OLEDDisplay.h), "BLACK")
    draw = ImageDraw.Draw(image)

    for x in range(OLEDDisplay.h-1, int((OLEDDisplay.h-1)/2), -6):
        draw.rectangle([(x, x), ((OLEDDisplay.w-1) - x, (OLEDDisplay.h-1) - x)], fill="BLUE", outline="BLUE")
        draw.rectangle([(x, x), ((OLEDDisplay.w-1) - x, (OLEDDisplay.h-1) - x)], fill=None, outline="YELLOW")
    OLEDDisplay.Display_Image(image)
    time.sleep(2.0)

def test_OLEDDisplay_Circles(OLEDDisplay):
    """
    Display Test Circles
    """
    image = Image.new("RGB", (OLEDDisplay.w, OLEDDisplay.h), "BLACK")
    draw = ImageDraw.Draw(image)

    draw.ellipse([(0, 0), (OLEDDisplay.w - 1, OLEDDisplay.h - 1)], fill="BLUE", outline="BLUE")
    OLEDDisplay.Display_Image(image)
    time.sleep(0.5)
    for r in range(0, int(OLEDDisplay.w/2) + 4, 4):
        draw.ellipse([(r, r), ((OLEDDisplay.w-1) - r, (OLEDDisplay.h-1) - r)], fill=None, outline="YELLOW")
    OLEDDisplay.Display_Image(image)
    time.sleep(2.0)

def test_OLEDDisplay_Triangles(OLEDDisplay):
    """
    Display Test Triangles
    """
    image = Image.new("RGB", (OLEDDisplay.w, OLEDDisplay.h), "BLACK")
    draw = ImageDraw.Draw(image)

    for i in range(0, int(OLEDDisplay.w/2), 4):
        draw.line([(i, OLEDDisplay.h - 1 - i), (OLEDDisplay.w/2, i)], fill=(255 - i*4, i*4, 255 - i*4), width=1)
        draw.line([(i, OLEDDisplay.h - 1 - i), (OLEDDisplay.w - 1 - i, OLEDDisplay.h - 1 - i)], fill=(i*4, i*4, 255 - i*4), width=1)
        draw.line([(OLEDDisplay.w - 1 - i, OLEDDisplay.h - 1 - i), (OLEDDisplay.w/2, i)], fill=(i*4, 255 - i*4, i*4), width=1)
        OLEDDisplay.Display_Image(image)
    time.sleep(2.0)

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
    Display_Picture(OLEDDisplay, "picture1.jpg")
    time.sleep(2.0)

def test_OLEDDisplay_Picture2(OLEDDisplay):
    """
    Display Test Picture "picture2.jpg"
    """
    Display_Picture(OLEDDisplay, "picture2.jpg")
    time.sleep(2.0)

def test_OLEDDisplay_Picture3(OLEDDisplay):
    """
    Display Test Picture "picture3.jpg"
    """
    Display_Picture(OLEDDisplay, "picture3.jpg")
    time.sleep(2.0)
