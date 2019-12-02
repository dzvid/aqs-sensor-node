import time

from environs import Env

from sensors.bmp280 import BMP280
from sensors.dht11 import DHT11
from sensors.mq135 import MQ135
from sensors.mq131 import MQ131

# Load enviroment variables
env = Env()
env.read_env()


class SensingModule:

    def __init__(self):
        self._dht = DHT11()
        self._bmp = BMP280()
        self._mq131 = MQ131()
        self._mq135 = MQ135()

    def calibrate_sensors(self):
        self._dht.calibrate()
        self._bmp.calibrate()
        # Since the calibration time is the same for the mq sensors
        # you can call the base class calibrate method from mq131 or mq135
        # self._mq135.calibrate()
        # self._mq131.calibrate()

    def calibrate_mq135_ro(self):

        current_humidity = self._dht.get_humidity()
        current_temperature = self._bmp.get_temperature()

        if(current_humidity is not None and current_temperature is not None):
            self._mq135.calibrate_ro(
                current_humidity=current_humidity, current_temperature=current_temperature)
        else:
            print("Could not get current humidity/temperature \
                   value from sensors, try again...")

    def calibrate_mq131_ro(self):

        current_humidity = self._dht.get_humidity()
        current_temperature = self._bmp.get_temperature()

        if(current_humidity is not None and current_temperature is not None):
            self._mq131.calibrate_ro(
                current_humidity=current_humidity, current_temperature=current_temperature)
        else:
            print("Could not get current humidity/temperature \
                   value from sensors, try again...")

    def read_sensors(self):
        """
        Read the sensors. If a error happens, returns None.
        WARNING: The reading method stays locked until it gets a valid humity reading from DHT11
        """

        # Read humidity from DHT11. Sometimes DHT11 will not return a valid humidity reading.
        # So it keeps trying to read humidity value until it gets a valid reading.
        # Takes a 2 second interval between readings following datasheet recomendations.
        try:
            humidity = None

            while humidity == None:
                humidity = self._dht.get_humidity()
                time.sleep(2)

            # Reads BMP280
            temperature = self._bmp.get_temperature()
            pressure = self._bmp.get_pressure()

            # Reads MQ135
            carbon_monoxide = self._mq135.get_carbon_monoxide(
                current_humidity=humidity, current_temperature=temperature)

            # Reads MQ131
            ozone = self._mq131.get_ozone(
                current_humidity=humidity, current_temperature=temperature, current_pressure=pressure)

            # Boilerplate
            pm2_5 = None
            pm10 = None

            # Returns a dict containing the reading
            reading = dict()

            reading['humidity'] = humidity
            reading['temperature'] = temperature
            reading['pressure'] = pressure
            reading['carbon_monoxide'] = carbon_monoxide
            reading['ozone'] = ozone
            reading['pm2_5'] = pm2_5
            reading['pm10'] = pm10

            return reading

        except (ValueError, RuntimeError) as e:
            print("Failed to get sensors reading, try again...\n", e)
            return None
