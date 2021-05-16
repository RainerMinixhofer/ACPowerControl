#!/usr/bin/python3
# -*- coding: utf-8 -*-
#pylint: disable=C0103,C0301,R0914,R0915
"""
Test 1.5Inch OLED Display control via SSD1351 Controller

Created on Sat Aug 29 22:12:34 2020

@author: Rainer Minixhofer
"""

import time
import asyncio
import evdev #pylint: disable=E0401
#--------------Tree Library----------------#
from treelib import Tree  #pylint: disable=E0401
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

@pytest.fixture(name='InputDevices')
def fixture_InputDevices():
    """
    initializes interface to input devices through evdev driver interface
    """

    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    #Filter the rotary encoder and the button device from the devices list
    devices = [dev for dev in devices if dev.name.split('@')[0] in ['button','rotary']]

    yield devices
    del devices

@pytest.fixture(name='suspend_capturing')
def fixture_suspend_capturing(pytestconfig):
    """
    fixture for suspending capturing to wait for hardware changes
    """
    class suspend_guard:
        """
        Subclass for suspending
        """
        def __init__(self):
            self.capmanager = pytestconfig.pluginmanager.getplugin('capturemanager')
        def __enter__(self):
            self.capmanager.suspend_global_capture(in_=True)
        def __exit__(self, _1, _2, _3):
            self.capmanager.resume_global_capture()

    yield suspend_guard()

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

    draw.text((0, 12), 'ACPower', fill="BLUE", font=font)
    draw.text((0, 36), 'RasPi', fill="BLUE", font=font)
    draw.text((20, 72), '1.5 inch', fill="CYAN", font=font)
    draw.text((10, 96), 'R', fill="RED", font=font)
    draw.text((25, 96), 'G', fill="GREEN", font=font)
    draw.text((40, 96), 'B', fill="BLUE", font=font)
    draw.text((55, 96), ' OLED', fill="CYAN", font=font)

    OLEDDisplay.Display_Image(image)
    time.sleep(2.0)

def test_OLEDDisplay_Menu(OLEDDisplay):
    """
    Display Menu Text
    """
    image = Image.new("RGB", (OLEDDisplay.w, OLEDDisplay.h), "BLACK")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('cambriab.ttf', 16)

    menu = ['Menu Line '+str(i) for i in range(5)]

    for sel in list(range(len(menu))) + list(range(len(menu)-1))[::-1]:
        width, height = font.getsize(menu[sel])
        draw.rectangle([(OLEDDisplay.w-width,12+sel*height), (OLEDDisplay.w, 12+(sel+1)*height)], fill="WHITE")
        for idx, line in enumerate(menu):
            width, height = font.getsize(line)
            draw.text((OLEDDisplay.w-width,12+idx*height), line, fill="BLUE", font=font)
        OLEDDisplay.Display_Image(image)
        time.sleep(0.5)
        draw.rectangle([(OLEDDisplay.w-width,12+sel*height), (OLEDDisplay.w, 12+(sel+1)*height)], fill="BLACK")

    time.sleep(0.5)

@pytest.mark.interactive
def test_OLEDDisplay_Menu_Encoder(OLEDDisplay, InputDevices, suspend_capturing):
    """
    Test Interaction between Display and KY40 Rotary Encoder with async encoder
    readout using a Menu
    """
    image = Image.new("RGB", (OLEDDisplay.w, OLEDDisplay.h), "BLACK")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('cambriab.ttf', 16)

    menu = Tree()
    menu.create_node('Root','root') #root
    for i in range(5):
        menu.create_node('Menu '+str(i),'menu_'+str(i), parent='root')
        for j in range(4):
            if i == 0 and j == 0:
                mstring = 'Menu '
            else:
                mstring = 'Item '
            menu.create_node(mstring+str(i)+'.'+str(j), \
                             'menu_'+str(i)+'.'+str(j), parent='menu_'+str(i))
        menu.create_node('Up','up_'+str(i), parent='menu_'+str(i))
    for i in range(4):
        menu.create_node('Item 0.0.'+str(i), 'menu_0.0.'+str(i), parent='menu_0.0')
    menu.create_node('Up','up_0.0', parent='menu_0.0')
    menu.create_node('Exit','menu_6', parent='root')
    menu.show(key=lambda x: x.identifier, idhidden=False)

    def plot_menu(parent, sel, color="BLUE"):
        nonlocal font
        nonlocal draw
        nonlocal image
        nonlocal menu

        lines = [line.tag for line in menu.children(parent)]
        [width, height] = map(list, zip(*[font.getsize(line) for line in lines]))
        width = max(width)
        height = max(height)
        x0 = OLEDDisplay.w-width
        y0 = 12
        draw.rectangle([(0, 0),(OLEDDisplay.w, OLEDDisplay.h)], fill="BLACK")

        draw.rectangle([(x0, y0 + sel*height), (OLEDDisplay.w, y0 + (sel+1)*height)], fill="WHITE")
        for idx, line in enumerate(lines):
            width, height = font.getsize(line)
            draw.text((x0, y0 + idx*height), line, fill=color, font=font)
        OLEDDisplay.Display_Image(image)

    def get_menu_nodename(parent, sel):
        return menu.children(parent)[sel].identifier

    def get_menu_len(parent, sel):
        return len(menu.siblings(get_menu_nodename(parent, sel))) + 1

    def menu_has_childs(parent, sel):
        return menu.is_branch(get_menu_nodename(parent, sel)) != []

    parent = 'root'
    selpos = 0
    plot_menu(parent, selpos)

    loop = asyncio.get_event_loop()

    async def handle_events(device):
        nonlocal parent
        nonlocal selpos
        nonlocal loop

        async for event in device.async_read_loop():
            event = evdev.util.categorize(event)
            if isinstance(event, evdev.events.RelEvent):
                print('Rotate captured')
                menulen = get_menu_len(parent, selpos)
                selpos = selpos + event.event.value
                if selpos < 0:
                    selpos = 0
                    print('selpos too small')
                elif selpos >= menulen:
                    selpos = menulen - 1
                    print('selpos too large')
                else:
                    plot_menu(parent, selpos)
                print('Position', selpos)
            elif isinstance(event, evdev.events.KeyEvent):
                if event.keycode == "KEY_ENTER" and event.keystate == event.key_down:
                    print('Key-Down captured')
                    print('Menu with childs', menu_has_childs(parent, selpos))
                    menulen = get_menu_len(parent, selpos)
                    if selpos == menulen - 1:
                        if parent == 'root':
                            loop.stop()
                        else:
                            # Store old parent identifier for later use
                            oldparent = menu.get_node(parent).identifier
                            # Assign new parent
                            parent = menu.parent(parent).identifier
                            # Get list of identifiers of all new menu items
                            newnodes = [node.identifier for node in menu.children(parent)]
                            # Assign position of old parent identifier to selpos
                            selpos = newnodes.index(oldparent)
                            plot_menu(parent, selpos)
                    elif menu_has_childs(parent, selpos):
                        parent = menu.children(parent)[selpos].identifier
                        selpos = 0
                        plot_menu(parent, selpos)

    with suspend_capturing:
        print("Please rotate encoder to setlect menu items in display.\n"
              "Press encoder button to enter submenues and\n"
              "select exit menu item to end test\n")
        for device in InputDevices:
            asyncio.ensure_future(handle_events(device))

        loop.run_forever()
        draw.rectangle([(0, 0),(OLEDDisplay.w, OLEDDisplay.h)], fill="BLACK")
        OLEDDisplay.Display_Image(image)

@pytest.mark.interactive
def test_OLEDDisplay_Settings(OLEDDisplay, InputDevices, suspend_capturing):
    """
    Test Interaction between Display and KY40 Rotary Encoder unsing async encoder
    readout using a voltage setting
    """
    image = Image.new("RGB", (OLEDDisplay.w, OLEDDisplay.h), "BLACK")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('cambriab.ttf', 30)

    def plot_voltage(voltage, color="BLUE"):
        nonlocal font
        nonlocal draw
        nonlocal image

        vstring = str(voltage)+'V/1A'
        width, height = font.getsize(vstring)
        x0 = (OLEDDisplay.w-width)//2
        y0 = (OLEDDisplay.h-height)//2
        draw.rectangle([(0, y0),(OLEDDisplay.w, y0 + height)], fill="BLACK")
        draw.text((x0, y0), vstring, fill=color, font=font)
        OLEDDisplay.Display_Image(image)

    vvalue = 0.5
    plot_voltage(vvalue)

    loop = asyncio.get_event_loop()

    async def handle_events(device):
        nonlocal vvalue
        nonlocal loop

        async for event in device.async_read_loop():
            event = evdev.util.categorize(event)
            if isinstance(event, evdev.events.RelEvent):
                vvalue = vvalue + event.event.value * 0.5
                if vvalue < 0.5:
                    vvalue = 0.5
                if vvalue > 30.0:
                    vvalue = 30.0
                plot_voltage(vvalue)
            elif isinstance(event, evdev.events.KeyEvent):
                plot_voltage(vvalue, color="RED")
                if event.keycode == "KEY_ENTER" and event.keystate == event.key_up:
                    loop.stop()

    with suspend_capturing:
        print("Please rotate encoder to set voltage value in display.\n"
              "Press encoder button to change text color to red and\n"
              "depress to end test\n")

        for device in InputDevices:
            asyncio.ensure_future(handle_events(device))

        loop.run_forever()
        draw.rectangle([(0, 0),(OLEDDisplay.w, OLEDDisplay.h)], fill="BLACK")
        OLEDDisplay.Display_Image(image)

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
