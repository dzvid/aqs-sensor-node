from environs import Env

from .mq import MQSensor

# Load enviroment variables
env = Env()


class MQ135(MQSensor):

    def __init__(self):
        # Sensor parameters
        self._NAME = env.str('MQ135_NAME', default=None)
        self._R1 = env.float('MQ135_R1', default=None)
        self._R2 = env.float('MQ135_R2', default=None)
        self._MQ_ADC_PIN = env.int('MQ135_MQ_ADC_PIN', default=None)
        self._RL_VALUE = env.float('MQ135_RL_VALUE', default=None)
        self._RO_CLEAN_AIR = env.float('MQ135_RO_CLEAN_AIR', default=None)
        self._A_EXPO = env.float('MQ135_A_EXPO', default=None)
        self._M_EXPO = env.float('MQ135_M_EXPO', default=None)
        self._RSRO_CLEAN_AIR = env.float('MQ135_RSRO_CLEAN_AIR', default=None)
        self._MIN_CONCENTRATION = env.float(
            'MQ135_MIN_CONCENTRATION', default=None)
        self._MAX_CONCENTRATION = env.float(
            'MQ135_MAX_CONCENTRATION', default=None)
        self._MIN_HUMIDITY = env.float(
            'MQ135_MIN_HUMIDITY', default=None)
        self._MAX_HUMIDITY = env.float(
            'MQ135_MAX_HUMIDITY', default=None)
        self._MIN_TEMPERATURE = env.float(
            'MQ135_MIN_TEMPERATURE', default=None)
        self._MAX_TEMPERATURE = env.float(
            'MQ135_MAX_TEMPERATURE', default=None)

        super().__init__(NAME=self._NAME, R1=self._R1, R2=self._R2, MQ_ADC_PIN=self._MQ_ADC_PIN, RL_VALUE=self._RL_VALUE, RO_CLEAN_AIR=self._RO_CLEAN_AIR, A_EXPO=self._A_EXPO,
                         M_EXPO=self._M_EXPO, RSRO_CLEAN_AIR=self._RSRO_CLEAN_AIR, MIN_CONCENTRATION=self._MIN_CONCENTRATION, MAX_CONCENTRATION=self._MAX_CONCENTRATION,
                         MAX_HUMIDITY=self._MAX_HUMIDITY, MIN_HUMIDITY=self._MIN_HUMIDITY,
                         MAX_TEMPERATURE=self._MAX_TEMPERATURE, MIN_TEMPERATURE=self._MIN_TEMPERATURE)

    def calibrate(self):
        """
        The MQ sensor needs an warmup time before taking a reading
        (this is not burn-in time). 
        """
        super().calibrate()

    def calibrate_ro(self):
        """
        Returns to stdout the Ro value in clean air if the sensor is in working temperature and humidty range.
        Otherwise, returns None

        Assuming that the sensor is in clean air, the method gets the gas
        sensor resistance (RS) in clean air, then it divides by RSRO_CLEAN_AIR 
        factor to obtain the Ro resistance value in clean air.
        """
        return super().calibrate_ro()

    def get_carbon_monoxide(self,  current_humidity=None, current_temperature=None):
        """
        Returns the carbon monoxide value in ppm units. 

        Returns None, when:
          - The sensor MQ sensor is not in valid environment working conditions.

          OR

          - The gas concentration is out of range of the sensor sensibility.


        Parameters
        ----------
        current_humidity: float
          Humidity in percentage.

        current_temperature: float
          Temperature in degrees Celsius.
        """

        if(current_humidity is None):
            raise ValueError('Humidity value must be informed')
        if(current_temperature is None):
            raise ValueError('Temperature value must be informed')

        return super().get_reading(current_humidity, current_temperature)
