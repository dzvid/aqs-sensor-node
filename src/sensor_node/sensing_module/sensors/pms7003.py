import time

from environs import Env
from pms7003 import Pms7003Sensor, PmsSensorException

from .sensor import Sensor


# Load enviroment variables
env = Env()
env.read_env()


class PMS7003(Sensor):
    """
    Class representing a PMS7003 sensor.
    """

    def __init__(self):
        # Get PMS7003 parameters from environment configs (.env)
        self._CALIBRATION_TIME = env.int(
            'PMS7003_CALIBRATION_TIME', default=None)
        self._UART_SERIAL_ADDRESS = env.str(
            'PMS7003_UART_SERIAL_ADDRESS', default=None)
        self._MIN_HUMIDITY = env.float('PMS7003_MIN_HUMIDITY', default=None)
        self._MAX_HUMIDITY = env.float('PMS7003_MAX_HUMIDITY', default=None)
        self._MIN_TEMPERATURE = env.float(
            'PMS7003_MIN_TEMPERATURE', default=None)
        self._MAX_TEMPERATURE = env.float(
            'PMS7003_MAX_TEMPERATURE', default=None)

        if(self._CALIBRATION_TIME is None):
            raise ValueError("PMS7003_CALIBRATION_TIME value must be declared")
        if(self._UART_SERIAL_ADDRESS is None):
            raise ValueError(
                "PMS7003_UART_SERIAL_ADDRESS value must be declared")
        if(self._MIN_HUMIDITY is None):
            raise ValueError("PMS7003_MIN_HUMIDITY value must be declared")
        if(self._MAX_HUMIDITY is None):
            raise ValueError("PMS7003_MAX_HUMIDITY value must be declared")
        if(self._MIN_TEMPERATURE is None):
            raise ValueError("PMS7003_MIN_TEMPERATURE value must be declared")
        if(self._MAX_TEMPERATURE is None):
            raise ValueError("PMS7003_MAX_TEMPERATURE value must be declared")

        # Creates a sensor instance
        self._pms_sensor = Pms7003Sensor(self._UART_SERIAL_ADDRESS)

    def calibrate(self):
        """
        The PMS7003 sensor needs 30 seconds initialization before returning stable data.
        """
        print(
            'Calibrating Sensor PMS7003 ({0} seconds)...'.format(self._CALIBRATION_TIME))

        time.sleep(self._CALIBRATION_TIME)

        print(
            'Calibrating Sensor PMS7003 ({0} seconds)... done!'.format(self._CALIBRATION_TIME))

    def _check_temperature_range(self, current_temperature=None):
        """
        Returns True if current temperature is in the temperature working condition range of the sensor.
        Otherwise, returns False.
        """
        if(current_temperature >= self._MIN_TEMPERATURE and current_temperature <= self._MAX_TEMPERATURE):
            return True
        return False

    def _check_humidity_range(self, current_humidity=None):
        """
        Returns True if current humidity is in the humidity working condition range of the sensor.
        Otherwise, returns False.
        """
        if(current_humidity >= self._MIN_HUMIDITY and current_humidity < self._MAX_HUMIDITY):
            return True
        return False

    def _check_working_conditions(self, current_humidity=None, current_temperature=None):
        """
        Return True if the sensor is in environment working range. Otherwise, returns False.
        """
        if (self._check_temperature_range(current_temperature) and self._check_humidity_range(current_humidity)):
            return True
        return False

    def get_particulate_matter(self, current_humidity=None, current_temperature=None):
        """
        Returns a dict containing the particulate matter values measured by the PMS7003.
        The value for PM 2.5 has the 'pm2_5' alias and PM 10 has the 'pm10' alias.

        Return None for both parameters when the sensor is out of environment working range.

        Raises an exception when there is a problem in the communication with sensor to get a reading.
        """

        if(current_humidity is None):
            raise ValueError('PMS7003: Humidity value must be informed')
        if(current_temperature is None):
            raise ValueError('PMS7003: Temperature value must be informed')

        try:

            reading = dict()

            # Initialize the parameters measured as None (invalid)
            reading['pm2_5'] = None
            reading['pm10'] = None

            # Check if environment working conditions is not good
            if not self._check_working_conditions(current_humidity=current_humidity, current_temperature=current_temperature):
                return reading

            # If environment is ok, try get sensor reading
            reading = self._pms_sensor.read()

            return reading

        except PmsSensorException:
            raise PmsSensorException(
                'Problem reading PMs7003 sensor, communication error that is \
                unlikely to re-occur(e.g. serial connection glitch). \
                Prevents from returning corrupt measurements.')
