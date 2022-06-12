# Instructions on Raspi Initialization

## Enabling file access to user home directory to be able to remotely edit python scripts with e.g. Spyder

First install samba with

    sudo apt install samba samba-common-bin
    
Edit Samba’s config files to make the home directory of the respective user writable remotely.

    sudo nano /etc/samba/smb.conf
    
 The following lines in the file smb.conf need to be adapted as shown below
 
```
[homes]
   comment = Home Directories
   browseable = yes
   writeable = yes
   only guest = no
   read only = no
```

furthermore the sections [printers] and [print$] should be commented out with an semicolon ;.
Then test the configuration file with

    testparm /etc/samba/smb.conf

We need to set a password for the standard user of the pi to enable access to its home directory

    sudo smbpasswd -a <standard user>
    
Finally restart samba with

    sudo systemctl restart smbd.service
    sudo systemctl restart nmbd.service

The home shares should be addressable through the usual \\\<server>\<username> URI format.

## Enabling I2C access to MCP23017 port expander and the INA260 power meter:

The following commands have been taken from [this page](https://tutorials-raspberrypi.de/raspberry-pi-gpios-erweitern-mittels-i2c-port-expander/)

    sudo raspi-config

Activate I2C under „Interfacing Options“ > „I2C“.

In the file /boot/config.txt there should be now a line:

    dtparam=i2c_arm=on
    
add here an additional parameter to enable 400kB/sec high speed I2C:

    dtparam=i2c_arm=on,i2c_arm_baudrate=400000

Then restart the RasPi

    sudo shutdown -r now
    
Check if I2C is really running on 400kB/sec by executing the following script (e.g. name it i2cspeed.sh and make it executable

```bash
#!/bin/bash
var="$(xxd /sys/class/i2c-adapter/i2c-1/of_node/clock-frequency | awk -F': ' '{print $2}')"
var=${var//[[:blank:].\}]/}
printf "%d\n" 0x$var
```

the result should be `400000`.

Check I2C access to the port expander and the power meter:

    sudo i2cdetect -y 1
    
It should show an I2C adress at 0x20 if A0 to A2 of the MCP23017 has been grounded. Furthermore address 0x40 of the INA260 should be shown.

## Initialize the MCP23017 and check it's accessability

We have to set the reset line of the MCP23017 (connected to BCM4) to output and then high to enable the chip

    gpio -g mode 4 out
    gpio -g write 4 1

Check the pin state with

    gpio readall

Now set all Pins of GPA and GPB of MCP23017 to output

    sudo i2cset -y 1 0x20 0x00 0x00
    sudo i2cset -y 1 0x20 0x01 0x00
    
Then we can switch the first relais connected to port GPA with:

    sudo i2cset -y 1 0x20 0x14 0x01
    
and e.g. the last (8th) with

    sudo i2cset -y 1 0x20 0x14 0x80
    
The same commands for the relais connected to port GPB are:

    sudo i2cset -y 1 0x20 0x15 0x01
    sudo i2cset -y 1 0x20 0x15 0x80
    
With the two commands

    sudo i2cset -y 1 0x20 0x14 0x00
    sudo i2cset -y 1 0x20 0x15 0x00
    
the two relais cards are set back to zero.

## Check accessability and functionality of the INA260 power meter:

Since the I2C address is 0x40 (see above) without changes on the jumpers A0 and A1 on the INA260 board we'll use this address for accessing the INA260 power meter registers.

The register definition can be found in Table 4 of Section 8.6 of the [INA260 Datasheet](https://www.ti.com/lit/ds/symlink/ina260.pdf).

| Pointer Adress Hex | Register Name            | Function                                                                   | Power-On Reset Value | Type |
| :----------------: | :----------------------: | :----------------------------------------------- | :---------------------------: | :-----: |
| 00h                | Configuration Register   | All-Register reset, shut voltage and bus<br />voltage ADC conversion times and<br />averaging, operating mode. | 6127                                      | R/W |
| 01h                | Current Register         | Contains the value of the current flowing<br />through the shunt resistor. | 0000 | R |
| 02h                | Bus Voltage Register     | Bus voltage measurement data.                    | 0000                                       | R |
| 03h                | Power Register           | Contains the value of the calculated<br />power being delivered to the load. | 0000 | R |
| 06h                | Mask/Enable Register     | Alert configuration and Conversion<br />ready flag.| 0000 | R/W |
| 07h                | Alert Limit Register     | Contains the limit value to compare to<br />the selected Alert function. | 0000 | R/W |
| FEh                | Manufacturer ID Register | Contains unique manufacturer identification number. | 5449 | R |
| FFh                | Die ID Register          | Contains unique die identification number.       | 2270 | R |

We now test read/wire from/to the INA260.

We use the i2cget command on the RasPi to read the registers. The command

    i2cget -y 1 0x40 0x00 w
    
should result in the power on reset value of 0x6127 but given as big endian (0x2761).
If we want to reset the device we have to set the reset bit (15) in register 00h with the command

    i2cset -y 1 0x40 0x27E1
    
The bit self-clears and thus we have 0x6127 again in this register after the reset.

The command

    i2cget -y 1 0x40 0x01 w
    
should yield a value between 0xffff and 0x0001 (again in big endian given as 0xffff and 0x0100) if no current flowing (noise of readout is causing fluctuation by one bit. The command

    i2cget -y 1 0x40 0x02 w
    
should yield a similiar output for the bus voltage. The power can be read by 

    i2cget -y 1 0x40 0x03 w
    
and is usually 0x0000. The manufacturer ID Register and the Die ID register can be read out by the commands

    i2cget -y 1 0x40 0xFE w
    i2cget -y 1 0x40 0xFF w
    
and yield 0x5449 and 0x2270 respectively.

## Enable access to SPI controlled OLED Display

    sudo raspi-config

Activate SPI under „Interfacing Options“ > „SPI“.
Then restart the RasPi

    sudo shutdown -r now

Check if SPI driver has been enabled via:

    modprobe spi_bcm2835
   
should not return any error messages.


## Enable access to KY40-Encoder via Kernel Device Driver

This follows the explanation in [KY-040 Rotary Encoder with Linux on the Raspberry Pi](https://blog.ploetzli.ch/2018/ky-040-rotary-encoder-linux-raspberry-pi/)

First enter following line into */boot/config.txt*

    #enable rotary encoder
    dtoverlay=rotary-encoder,pin_a=21,pin_b=20,relative_axis=1
    dtoverlay=gpio-key,gpio=16,keycode=28,label="ENTER"
    
\<pin_a> specifies the CLK pin, \<pin_b> specifies the DT pin and \<gpio> the pin for the enter button switch.
Then reboot the RasPi. Warning first reboot may take a bit longer since the driver gets activated, so don't get impatient!
Then install the evtest tool and check out the encoder:

    sudo apt install evtest python3-evdev

The new device can be found under */dev/input/event0* and */dev/input/event1* button and axis respectively, and can be tested with

    evtest /dev/input/event0
    evtest /dev/input/event1

## Required Libraries for Project

Treelib (for menu in GUI):

    pip3 install treelib
    
evdev (driver for Rotary encoder see above section)

PIL (for OLED Display):

    sudo apt install python3-pil python3-pil.imagetk

pytest (for code testing):

    pip3 install pytest

The wiki uses [Markdown](/p/acpowercontrol/wiki/markdown_syntax/) syntax.
