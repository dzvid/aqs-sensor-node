import time

import Adafruit_DHT

from environs import Env

from .sensor import Sensor

# Load enviroment variables
env = Env()


class DHT11Exception(Exception):
    """
    Unable to get a reading from DHT11.
    """
    pass


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

    def get_humidity(self):
        """
        Returns a float percentage value representing the the humidity measured by the DHT11 sensor.
        According to the datasheet the time interval between taking consecutive readings
        must be of at least of 2 seconds.

        In most cases you'll always get back a temperature or humidity value when requested,
        but sometimes if there's electrical noise or the signal was interrupted in some way.
        Use the read_retry method which will retry up to 15 times to get a sensor reading
        (waiting 2 seconds between each retry).
        Note that sometimes you won't get a reading and
        the results will be null (because Linux can't
        guarantee the timing of calls to read the sensor).
        If this happens, the method returns None (and it is necessary to try again!).
        """

        # (Can take up to 30 seconds)
        humidity, _temperature = Adafruit_DHT.read_retry(
            self._sensor, self._pin)

        if humidity is not None:
            return round(humidity, 3)
        else:
            raise DHT11Exception("Reading from DHT failed. Try again!")
