import time

import Adafruit_DHT

from environs import Env

from .sensor import Sensor

# Load enviroment variables
env = Env()


class DHT11(Sensor):
    """
    Class to connect to the DHT11 sensor.
    """

    def __init__(self):
        self._sensor = Adafruit_DHT.DHT11

        self._pin = env.int('DHT11_PIN', default=None)

        if (self._pin is None):
            raise ValueError('DHT pin value must be informed.')

    def calibrate(self):
        """
        During the DHT11 booting time (when the circuit turns on), the datasheet 
        informs to wait 1 second before the sensor is able to respond to any commands.
        """
        print('Calibrating DHT11 sensor...')

        time.sleep(1)

        print('Calibrating DHT11 sensor...done!')

    @property
    def humidity(self):
        """
        Returns the humidity value measured by the DHT11 sensor. According to the datasheet
        the time interval between taking consecutive readings must be at least of 2 seconds.

        In most cases you'll always get back a temperature or humidity value when requested,
        but sometimes if there's electrical noise or the signal was interrupted in some way.  
        Use the read_retry method which will retry up to 15 times to get a sensor reading 
        (waiting 2 seconds between each retry).
        Note that sometimes you won't get a reading and
        the results will be null (because Linux can't
        guarantee the timing of calls to read the sensor).
        If this happens, the method returns None (and it is necessary to try again!).
        """

        humidity, _temperature = Adafruit_DHT.read_retry(
            self._sensor, self._pin)

        if humidity is not None:
            return humidity
        else:
            print("Reading from DHT failed. Try again!")
            return None
