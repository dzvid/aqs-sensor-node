from environs import Env

import Adafruit_DHT

from .sensor import Sensor

# Load enviroment variables
env = Env()


class DHT11Sensor(Sensor):

    def __init__(self, pin=None):
        self._sensor = Adafruit_DHT.DHT11

        self._pin = env.int('DHT11_PIN', default=None)

        if (self._pin is None):
            raise ValueError('DHT pin value must be informed.')

    def calibrate(self):
        pass

    def get_reading(self):
        """
        Returns the humidity value measured by the DHT11 sensor.

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
