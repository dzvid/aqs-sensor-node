import board
from adafruit_bme280 import basic as adafruit_bme280

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
        self._i2c_address = env.int("BME280_I2C_ADDRESS", default=None)
        if self._i2c_address is None:
            raise ValueError("BME280: Necessary to inform sensor i2c address!")

        self._local_sea_level = env.float(
            "BME280_LOCAL_SEA_LEVEL", default=None
        )
        if self._local_sea_level is None:
            raise ValueError(
                "BME280: Necessary to inform location sea level pressure!"
            )

        self._i2c = board.I2C()
        self._bme280 = adafruit_bme280.Adafruit_BME280_I2C(
            i2c=self._i2c, address=self._i2c_address
        )
        self._bme280.sea_level_pressure = self._local_sea_level
        print(
            "BME280: Setting sea-level pressure as {0} hPa.".format(
                self._local_sea_level
            )
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
