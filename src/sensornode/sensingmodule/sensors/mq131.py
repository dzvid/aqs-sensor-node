
from environs import Env

from .mq import MQSensor

# Load enviroment variables
env = Env()


class MQ131(MQSensor):

    def __init__(self):
        # Ozone properties
        self._molecular_weight = 48.0  # Ozone molecular weight 48 g/mol

        # Circuit parameters
        self._R1 = env.float('MQ131_R1')
        self._R2 = env.float('MQ131_R2')
        self._MQ_ADC_PIN = env.int('MQ131_MQ_ADC_PIN')
        self._RL_VALUE = env.float('MQ131_RL_VALUE')
        self._RO_CLEAN_AIR = env.float('MQ131_RO_CLEAN_AIR', default=None)
        self._A_EXPO = env.float('MQ131_A_EXPO')
        self._M_EXPO = env.float('MQ131_M_EXPO')
        self._RSRO_CLEAN_AIR = env.float('MQ131_RSRO_CLEAN_AIR')
        self._MIN_CONCENTRATION = env.float('MQ131_MIN_CONCENTRATION')
        self._MAX_CONCENTRATION = env.float('MQ131_MAX_CONCENTRATION')

        super().__init__(R1=self._R1, R2=self._R2, MQ_ADC_PIN=self._MQ_ADC_PIN, RL_VALUE=self._RL_VALUE, RO_CLEAN_AIR=self._RO_CLEAN_AIR, A_EXPO=self._A_EXPO,
                         M_EXPO=self._M_EXPO, RSRO_CLEAN_AIR=self._RSRO_CLEAN_AIR, MIN_CONCENTRATION=self._MIN_CONCENTRATION, MAX_CONCENTRATION=self._MAX_CONCENTRATION)

    def get_reading(self):
        """
        Returns the ozone value in ppb. Returns None when the gas concentration 
        is out of range of the sensor sensibility.
        """
        return super().get_reading()

    def get_ug_m3_reading(self):
        """
        Returns the ozone ppb value in µg/m³ units.

        The equation to convert ppm to µg/m³ for a Z ppm concentration of a given
        element/compost is:

        C = 40.9 * Z * molecular_weight(µg/m³)

        for a X ppb concentration:

        C = 0.0409 * X * molecular_weight(µg/m³)

        where:
        C: is the equivalent ppm value in µg/m³.
        Z: is the ppm concentration of a given
        element/compost.
        X: is the ppb concentration of a given
        element/compost.
        molecular_weight: is the molecular weight in gram/mole

        """
        ozone_ppb = self.get_reading()

        if ozone_ppb is not None:
            ozone_ug_m3 = 0.0409 * ozone_ppb * self._molecular_weight

            return round(ozone_ug_m3, 3)
        else:
            return None
