import busio
import digitalio
import board

import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn


class ADC:

    # Its the same spi bus, cs object and mcp object for all ADC instances.
    # The difference between instances is the channel attribute

    # create the spi bus
    _spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

    # create the cs (chip select)
    _cs = digitalio.DigitalInOut(board.D5)

    # create the mcp object
    _mcp = MCP.MCP3008(_spi, _cs)

    # ADC maximum resolution value
    ADC_MAX_RESOLUTION = 1023.0

    def __init__(self, pin_adc=None):

        # ADC channel value, be careful to not use one channel for more than one device!
        self._channel = None

        # Create an analog input channel on the MCP3008 according to pin_adc value
        if(pin_adc is None):
            raise ValueError('pin_adc needs to be informed.')
        elif(pin_adc == 0):
            self._channel = AnalogIn(type(self)._mcp, MCP.P0)
        elif (pin_adc == 1):
            self._channel = AnalogIn(type(self)._mcp, MCP.P1)
        elif (pin_adc == 2):
            self._channel = AnalogIn(type(self)._mcp, MCP.P2)
        elif (pin_adc == 3):
            self._channel = AnalogIn(type(self)._mcp, MCP.P3)
        elif (pin_adc == 4):
            self._channel = AnalogIn(type(self)._mcp, MCP.P4)
        elif (pin_adc == 5):
            self._channel = AnalogIn(type(self)._mcp, MCP.P5)
        elif (pin_adc == 1):
            self._channel = AnalogIn(type(self)._mcp, MCP.P6)
        elif (pin_adc == 1):
            self._channel = AnalogIn(type(self)._mcp, MCP.P7)
        else:
            raise ValueError(
                "Invalid pin value. Pin value must be an integer value between 0 and 7")

    def read_raw_value(self):
        """Returns the adc raw value for the pin informed as an integer."""

        # the raw ADC value is encoded on 16 bits to match other ADCs
        # It is necessary to shift the adc output 6 bits down to convert to 10 bits
        # as the MCP3008 only has 10 bits
        return self._channel.value >> 6

    def read_voltage(self):
        """Returns the voltage from the ADC pin as a floating point value."""
        # The voltage value is scaled 16 bits to remain consistent with other ADCs.
        return self._channel.voltage

    def read_adc_max_resolution(self):
        """Returns the adc max resolution value"""
        return self.ADC_MAX_RESOLUTION
