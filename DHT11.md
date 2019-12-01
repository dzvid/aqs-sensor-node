## Configure 1-Wire

1 - To enable the one-wire interface you need to add the following line to /boot/config.txt,
we are going to use GPIO 4 (pin 7) as the 1-Wire interface (the GPIO 4 is the default pin for 1-Wire):

```bash
dtoverlay=w1-gpio, gpiopin=4
```

Then reboot your pi.

2 - Now just to make sure the interface is enabled, type `sudo raspi-config` in terminal.
Go to `Interfacing Options`, then select 1-Wire, then select `yes` to enable the 1-Wire interface.
After finish the operation, reboot the pi.

3 - To check the list the devices that your Raspberry Pi has discovered via all
1-Wire busses (by default GPIO 4), run the following command in terminal:

```bash
  ls /sys/bus/w1/devices/
```

## Wiring

The DHT 11 Wiring to the Raspberry Pi board:

- DHT VCC (pin 1) to Pi 3V3
- DHT Data signal (pin 2) to Pi GPIO4
- DHT pin 3 not used.
- DHT GND (pin 4) to Pi GND

## Install Adafruit DHT Python library

Now it is time to install the python library made by Adafruit to read the DHT series of humidity and temperature sensors on a Raspberry Pi or Beaglebone Black. Check this [link](https://github.com/adafruit/Adafruit_Python_DHT) for the Adafruit library repository in Github.  
**In this tutorial it is necessary to use Python 3 and pip3!**

### Dependencies

For all platforms (Raspberry Pi and Beaglebone Black) make sure your system is able to compile and download Python extensions with pip. On Raspbian or Beaglebone Black's Debian/Ubuntu image you can ensure your system is ready by running one or two of the following sets of commands:

Python 3:

```bash
sudo apt-get update
sudo apt-get install python3-pip
sudo python3 -m pip install --upgrade pip setuptools wheel
```

### Installing the library using pip

1 - Use pip to install the library from PyPI. Load the virtual enviroment and run the following command on the terminal:

```bash
pip3 install Adafruit_DHT
```

### Compiling from source

If necessary to compile and install the library from the repository. First download the library source code from the [GitHub releases page](https://github.com/adafruit/Adafruit_Python_DHT/releases), unzipping the archive, and execute:

Python 3:

```bash
cd Adafruit_Python_DHT
sudo python3 setup.py install
```

You may also git clone the repository if you want to test an unreleased version:

```bash
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
```
