import board
import busio
import adafruit_bme280

from environs import Env

from .sensor import Sensor


# Load enviroment variables
env = Env()
env.read_env()


class BME280Exception(Exception):
    """
    Implies a problem with sensor communication that is unlikely to re-occur
    (e.g. I2C (or SPI) connection glitch or wiring problem).
    """

    pass


class BME280(Sensor):
    """
    Class that represents the BME280 Sensor.
    """

    def __init__(self):

        self._i2c = busio.I2C(board.SCL, board.SDA)
        self._bme280 = adafruit_bme280.Adafruit_BME280_I2C(
            i2c=self._i2c, address=0x76
        )

        # change BME280_LOCAL_SEA_LEVEL in .env to match the
        # location's pressure (hPa) at sea level
        # default is sea level pressure 1013.25
        self._local_sea_level = env.float(
            "BME280_LOCAL_SEA_LEVEL", default=None
        )

        # Set location's pressure (hPa) at sea level
        if self._local_sea_level is not None:
            self._bme280.seaLevelhPa = self._local_sea_level
        else:
            raise ValueError(
                "BME280: Necessary to inform location's pressure (in hPa) at sea level"
            )

    def calibrate(self):
        """
        Not necessary to calibrate the BME280.
        """
        print("BME280 not necessary to calibrate.")

    def get_pressure(self):
        """
        Returns pressure in hectoPascals (hPa).
        """
        try:

            return round(self._bme280.pressure, 3)

        except (OSError):
            raise BME280Exception(
                "I/O error: Problem reading BME280 sensor, communication \
                                  error that is unlikely to re-occur \
                                  (e.g. I2C (or SPI) connection glitch or wiring problem."
            )

    def get_temperature(self):
        """Returns temperature in degrees Celsius."""
        try:

            return round(self._bme280.temperature, 3)

        except (OSError):
            raise BME280Exception(
                "I/O error: Problem reading BME280 sensor, communication \
                                  error that is unlikely to re-occur \
                                  (e.g. I2C (or SPI) connection glitch \
                                  or wiring problem."
            )

    def get_humidity(self):
        """Returns humidity as a value between 0 and 100%."""
        try:

            return round(self._bme280.humidity, 3)

        except (OSError):
            raise BME280Exception(
                "I/O error: Problem reading BME280 sensor, communication \
                                  error that is unlikely to re-occur \
                                  (e.g. I2C (or SPI) connection glitch \
                                  or wiring problem."
            )
