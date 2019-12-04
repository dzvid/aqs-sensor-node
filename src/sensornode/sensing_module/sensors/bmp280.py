import board
import busio
import adafruit_bmp280

from environs import Env

from .sensor import Sensor


# Load enviroment variables
env = Env()


class BMP280Exception(Exception):
    """
    Implies a problem with sensor communication that is unlikely to re-occur
    (e.g. I2C (or SPI) connection glitch or wiring problem).
    """
    pass


class BMP280(Sensor):
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
                'BMP280: Necessary to inform location\'s pressure (in hPa) at sea level')

    def calibrate(self):
        """
        Not necessary to calibrate the BMP280.
        """
        print('BMP280 not necessary to calibrate.')

    def get_pressure(self):
        """
        The compensated pressure (current air pressure at your altitude)
        in hectoPascals (hPa). Returns None if pressure measurement is disabled.
        """
        try:

            return round(self._bmp_sensor.pressure, 3)

        except (OSError):
            raise BMP280Exception("I/O error: Problem reading BMP280 sensor, communication \
                                  error that is unlikely to re-occur \
                                  (e.g. I2C (or SPI) connection glitch or wiring problem.")

    def get_temperature(self):
        """The compensated temperature in degrees Celsius."""
        try:

            return round(self._bmp_sensor.temperature, 3)

        except (OSError):
            raise BMP280Exception("I/O error: Problem reading BMP280 sensor, communication \
                                  error that is unlikely to re-occur \
                                  (e.g. I2C (or SPI) connection glitch or wiring problem.")
