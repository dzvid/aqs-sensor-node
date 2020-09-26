import time

from environs import Env

from mq import MQSensor

# Load enviroment variables
env = Env()
env.read_env()


class MQ131(MQSensor):

    def __init__(self):
        # Ozone properties
        self._molecular_weight = 48.0  # Ozone molecular weight 48 g/mol

        # Sensor parameters
        self._NAME = env.str('MQ131_NAME', default=None)
        self._R1 = env.float('MQ131_R1', default=None)
        self._R2 = env.float('MQ131_R2', default=None)
        self._MQ_ADC_PIN = env.int('MQ131_MQ_ADC_PIN', default=None)
        self._RL_VALUE = env.float('MQ131_RL_VALUE', default=None)
        self._RO_CLEAN_AIR = env.float('MQ131_RO_CLEAN_AIR', default=None)
        self._A_EXPO = env.float('MQ131_A_EXPO', default=None)
        self._M_EXPO = env.float('MQ131_M_EXPO', default=None)
        self._RSRO_CLEAN_AIR = env.float('MQ131_RSRO_CLEAN_AIR', default=None)
        self._MIN_CONCENTRATION = env.float(
            'MQ131_MIN_CONCENTRATION', default=None)
        self._MAX_CONCENTRATION = env.float(
            'MQ131_MAX_CONCENTRATION', default=None)
        self._MIN_HUMIDITY = env.float(
            'MQ131_MIN_HUMIDITY', default=None)
        self._MAX_HUMIDITY = env.float(
            'MQ131_MAX_HUMIDITY', default=None)
        self._MIN_TEMPERATURE = env.float(
            'MQ131_MIN_TEMPERATURE', default=None)
        self._MAX_TEMPERATURE = env.float(
            'MQ131_MAX_TEMPERATURE', default=None)

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

    def calibrate_ro(self, current_humidity=None, current_temperature=None):
        """
        Returns to stdout the Ro value in clean air if the sensor is in working temperature and humidty range.
        Otherwise, returns None

        Assuming that the sensor is in clean air, the method gets the gas
        sensor resistance (RS) in clean air, then it divides by RSRO_CLEAN_AIR 
        factor to obtain the Ro resistance value in clean air.


        Parameters
        ----------
        current_humidity: float
          Humidity in percentage.

        current_temperature: float
          Temperature in degrees Celsius.
        """
        return super().calibrate_ro(current_humidity=current_humidity, current_temperature=current_temperature)

    def get_ozone(self, current_humidity=None, current_temperature=None):
        """
        Returns the ozone value in µg/m³ units. 

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

        #  To convert ppm or ppb to µg/m³ in 1 atm (= 1013.2051 hectPa = 760 mmHg) and 25°C

        #     The equation to convert ppm to µg/m³ for a Z ppm concentration of a given element/compost is:

        #     C = 40.9 * Z * molecular_weight (µg/m³)

        #     for a M ppb (ppm = ppb / 1000) concentration  (USED  IN THE CODE):

        #     C = 0.0409 * M * molecular_weight (µg/m³)

        #     where:
        #     C: is the equivalent ppm value in µg/m³.
        #     Z: is the ppm concentration of a given
        #     element/compost.
        #     M: is the ppb concentration of a given
        #     element/compost.
        #     molecular_weight: is the molecular weight of the element/compost in gram/mole.

        # Reads ozone value in ppb
        # The MQ sensor regression function for ozone returns the ppb value measured
        ozone_ppb = super().get_reading(current_humidity=current_humidity,
                                        current_temperature=current_temperature)

        if ozone_ppb is not None:
            ozone_ug_m3 = 0.0409 * ozone_ppb * self._molecular_weight

            return round(ozone_ug_m3, 3)
        else:
            return None
