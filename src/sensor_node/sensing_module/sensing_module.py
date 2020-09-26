import time

from environs import Env

from pms7003 import PmsSensorException
from sensors.bme280 import BME280Exception
from sensors.mq import MQSensorException

from sensors.bme280 import BME280
from sensors.mq135 import MQ135
from sensors.mq131 import MQ131
from sensors.pms7003 import PMS7003

from .reading import Reading

# Load enviroment variables
env = Env()
env.read_env()


class SensingModuleException(Exception):
    """
    Generic Sensing Module error.
    """


class SensingModuleCreationError(SensingModuleException):
    """
    Failed to create a Sensing Module instance.
    """


class SensingModule:
    """
    Class that represents the sensing module of the Sensor Node.
    """

    def __init__(self):

        try:
            self._bme280 = BME280()
            self._pms7003 = PMS7003()
            self._mq131 = MQ131()
            self._mq135 = MQ135()
        except ValueError as error:
            raise SensingModuleCreationError(
                'Failed to create the Sensing Module: ', error)

    def calibrate_sensors(self):
        self._bme280.calibrate()
        self._pms7003.calibrate()
        # Since the calibration time is the same for the mq sensors
        # you can call the base class calibrate method from mq131 or mq135
        # self._mq135.calibrate()
        self._mq131.calibrate()

    def calibrate_mq135_ro(self):
        """
        Calibrate Sensor MQ-135 Ro resistance value in clean air.
        """

        try:
            current_humidity = self._bme280.get_humidity()
            current_temperature = self._bme280.get_temperature()

            self._mq135.calibrate_ro(
                current_humidity=current_humidity, current_temperature=current_temperature)
        except (BME280Exception) as e:
            print("Could not get current humidity/temperature \
                   value from the sensor, try again...", e)
        except(MQSensorException, ValueError, RuntimeError) as e:
            print(e)

    def calibrate_mq131_ro(self):
        """
        Calibrate Sensor MQ-131 Ro resistance value in clean air.
        """
        try:
            current_humidity = self._bme280.get_humidity()
            current_temperature = self._bme280.get_temperature()

            self._mq131.calibrate_ro(
                current_humidity=current_humidity, current_temperature=current_temperature)
        except (BME280Exception) as e:
            print("Could not get current humidity/temperature \
                   value from the sensor, try again...", e)
        except(MQSensorException, ValueError, RuntimeError) as e:
            print(e)

    def read_sensors(self):
        """
        Read the sensors.
        Returns a reading, if the reading is successful.
        Returns None, if an error occurs when reading the sensors.
        """

        try:
            # The following comment is for when using DHT11 Sensor:
              # humidity = None
              # WARNING: using the loop below the reading method stays locked until
              #  it gets a valid humity reading from DHT11
              # Read humidity from DHT11. Sometimes DHT11 will not return a valid humidity reading.
              # So it keeps trying to read humidity value until it gets a valid reading.
              # Takes a 2 second interval between readings following datasheet recomendations.

              # while humidity == None:
              #     humidity = self._dht11.get_humidity()
              #     time.sleep(2)

              # Reads DHT11 (Can take up to 30 seconds)

            # Reads BME280
            relative_humidity = self._bme280.get_temperature()
            temperature = self._bme280.get_temperature()
            pressure = self._bme280.get_pressure()

            # Reads MQ135
            carbon_monoxide = self._mq135.get_carbon_monoxide(
                current_humidity=relative_humidity, current_temperature=temperature)

            # Reads MQ131
            ozone = self._mq131.get_ozone(
                current_humidity=relative_humidity, current_temperature=temperature)

            # Reads PMS7003
            particulate_matter = self._pms7003.get_particulate_matter(
                current_humidity=relative_humidity, current_temperature=temperature)

            return Reading(carbon_monoxide=carbon_monoxide, pm2_5=particulate_matter['pm2_5'], pm10=particulate_matter['pm10'], ozone=ozone, temperature=temperature, relative_humidity=relative_humidity, pressure=pressure)

        except (BME280Exception, MQSensorException, PmsSensorException, ValueError, RuntimeError) as e:
            print("Failed to get sensors reading, try again...\n", e)
            return None
