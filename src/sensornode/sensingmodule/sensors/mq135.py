from environs import Env

from .mq import MQSensor

# Load enviroment variables
env = Env()


class MQ135(MQSensor):

    def __init__(self):
        # Circuit parameters
        self._R1 = env.float('MQ135_R1')
        self._R2 = env.float('MQ135_R2')
        self._MQ_ADC_PIN = env.int('MQ135_MQ_ADC_PIN')
        self._RL_VALUE = env.float('MQ135_RL_VALUE')
        self._RO_CLEAN_AIR = env.float('MQ135_RO_CLEAN_AIR', default=None)
        self._A_EXPO = env.float('MQ135_A_EXPO')
        self._M_EXPO = env.float('MQ135_M_EXPO')
        self._RSRO_CLEAN_AIR = env.float('MQ135_RSRO_CLEAN_AIR')
        self._MIN_CONCENTRATION = env.float('MQ135_MIN_CONCENTRATION')
        self._MAX_CONCENTRATION = env.float('MQ135_MAX_CONCENTRATION')

        super().__init__(R1=self._R1, R2=self._R2, MQ_ADC_PIN=self._MQ_ADC_PIN, RL_VALUE=self._RL_VALUE, RO_CLEAN_AIR=self._RO_CLEAN_AIR, A_EXPO=self._A_EXPO,
                         M_EXPO=self._M_EXPO, RSRO_CLEAN_AIR=self._RSRO_CLEAN_AIR, MIN_CONCENTRATION=self._MIN_CONCENTRATION, MAX_CONCENTRATION=self._MAX_CONCENTRATION)

    def get_reading(self):
        """
        Returns the carbon monoxide value in ppm. Returns None when the gas concentration 
        is out of range of the sensor sensibility.
        """
        return super().get_reading()
