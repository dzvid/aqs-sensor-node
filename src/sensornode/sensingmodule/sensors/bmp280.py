import board
import busio
import adafruit_bmp280

from environs import Env

from .sensor import Sensor


# Load enviroment variables
env = Env()


class BMP280:
    """
    Class that represents the BMP280 Sensor.
    """

    def __init__(self):

        self._i2c = busio.I2C(board.SCL, board.SDA)
        self._bmp_sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c=self._i2c)

        # change BMP280_LOCAL_SEA_LEVEL in .env to match the location's pressure (hPa) at sea level
        self._local_sea_level = env.float(
            'BMP280_LOCAL_SEA_LEVEL', default=None)

        # Set location's pressure (hPa) at sea level
        if(self._local_sea_level is not None):
            self._bmp_sensor.seaLevelhPa = self._local_sea_level
        else:
            raise ValueError(
                'Necessary to inform location\'s pressure (in hPa) at sea level')

    @property
    def pressure(self):
        """
        The compensated pressure (current air pressure at your altitude)
        in hectoPascals (hPa). Returns None if pressure measurement is disabled.
        """
        return self._bmp_sensor.pressure

    @property
    def temperature(self):
        """The compensated temperature in degrees Celsius."""
        return self._bmp_sensor.temperature
