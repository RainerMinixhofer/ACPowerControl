#!/usr/bin/python3
"""
KY40EncoderTest.py tests basic functionality of reading the KY-40
Encoder with the RasPi using an input device driver
(see https://blog.ploetzli.ch/2018/ky-040-rotary-encoder-linux-raspberry-pi/)
"""
# pylint: disable=C0103,W0603
# coding=utf-8
# Needed modules will be imported and configured
from __future__ import print_function

import selectors
import asyncio
import evdev #pylint: disable=E0401
import pytest

text_bold = '\033[1m'
text_unbold = '\033[0m'

@pytest.fixture(name='InputDevices')
def fixture_InputDevices():
    """
    initializes interface to input devices through evdev driver interface
    """
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    #Filter the rotary encoder and the button device from the devices list
    devices = [dev for dev in devices if dev.name.split('@')[0] in ['button','rotary']]
    selector = selectors.DefaultSelector()

    for dev in devices:
        selector.register(dev, selectors.EVENT_READ)

    yield selector
    del selector

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

@pytest.mark.interactive
def test_KY40Encoder_rotation_sync(InputDevices,suspend_capturing):
    """
    Test for rotation using synchronous readout. Asks user to rotate 10 times right and
    then 10 times left. Checks if the right number of events is captured
    """
    value = 0
    done = False

    with suspend_capturing:
        print("Please rotate encoder " + text_bold + "10" + text_unbold + \
              " times clockwise and then " + text_bold + "10" + text_unbold + \
              " times counterclockwise.\n")
        print("Position Value: {:02d}".format(value),end='\r')
        while not done:
            for key, _ in InputDevices.select():
                device = key.fileobj
                for event in device.read():
                    event = evdev.util.categorize(event)
                    if isinstance(event, evdev.events.RelEvent):
                        value = value + event.event.value
                        print("Position Value: {:02d}".\
                              format(value), end='\r')
                        if value == 0:
                            done = True
                            break
                    elif isinstance(event, evdev.events.KeyEvent):
                        if event.keycode == "KEY_ENTER" and event.keystate == event.key_up:
                            done = True
                            break
        print("\n")

@pytest.mark.interactive
def test_KY40Encoder_rotation_async(InputDevices,suspend_capturing):
    """
    Test for rotation using asyncio. Asks user to rotate 10 times right and
    then 10 times left. Checks if the right number of events is captured
    """
    value = 0
    loop = asyncio.get_event_loop()
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

    async def handle_events(device):
        nonlocal value
        nonlocal loop

        async for event in device.async_read_loop():
            event = evdev.util.categorize(event)
            if isinstance(event, evdev.events.RelEvent):
                value = value + event.event.value
                print("Position Value: {:02d}".\
                      format(value), end='\r')
                if value == 0:
                    loop.stop()
            elif isinstance(event, evdev.events.KeyEvent):
                if event.keycode == "KEY_ENTER" and event.keystate == event.key_up:
                    loop.stop()

    for device in devices:
        asyncio.ensure_future(handle_events(device))

    with suspend_capturing:
        print("Please rotate encoder " + text_bold + "10" + text_unbold + \
              " times clockwise and then " + text_bold + "10" + text_unbold + \
              " times counterclockwise.\n")
        print("Position Value: {:02d}\n".format(value))
        loop.run_forever()
