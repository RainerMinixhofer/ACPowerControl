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

import select
import evdev #pylint: disable=E0401

devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
devices = {dev.fd: dev for dev in devices}

value = 1
print("Value: {0}".format(value))

done = False
while not done:
    r, w, x = select.select(devices, [], [])
    for fd in r:
        for event in devices[fd].read():
            event = evdev.util.categorize(event)
            if isinstance(event, evdev.events.RelEvent):
                value = value + event.event.value
                print("Value: {0}".format(value))
            elif isinstance(event, evdev.events.KeyEvent):
                if event.keycode == "KEY_ENTER" and event.keystate == event.key_up:
                    done = True
                    break
