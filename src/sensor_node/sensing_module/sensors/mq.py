# -*- coding: utf-8 -*-

# Adapted from:
#   http://sandboxelectronics.com/?p=165
#   http://davidegironi.blogspot.com/2017/05/mq-gas-sensor-correlation-function.html#.XdyM5R-YXKa
import time

from environs import Env

from .sensor import Sensor
from .adc import ADC

# Load enviroment variables
env = Env()
env.read_env()


class MQSensorException(Exception):
    """
    Implies a problem with sensor communication that is unlikely to re-occur (e.g. connection glitch).
    Prevents from returning corrupt measurements, such as divison by zero error when VPIN returns 0 Volts
    which should not happen in practice, but sometimes there is a bad connection in the
    protoboard.
    """

    pass


class MQSensor(Sensor):
    """
    Base MQ-X Sensor object. This class reads the parameters and enables the
    sensor for continuous reads.
    """

    ######################### Hardware Related Macros #########################
    # Power supply value (in Volts)
    VCC = 5.0
    # Raspberry maximum input volta (in Volts)
    VCC_PI_INPUT_MAX = 3.3
    # Preheat time in seconds, usually 30 minutes
    PREHEAT_TIME = env.int("MQ_PREHEAT_TIME", default=None)
    if PREHEAT_TIME is None:
        raise ValueError("MQ_PREHEAT_TIME must be declared.")

    ######################### Software Related Macros #########################
    # Defines the amount of samples to be used during the calibration phase.
    CALIBRATION_SAMPLES = 10
    # Sets the time interval (in seconds) between samples during the calibration phase.
    CALIBRATION_SAMPLES_INTERVAL = 0.5
    # Defines the amount of samples to be used during the reading phase.
    READING_MODE_SAMPLES = 5
    # Sets the time interval (in seconds) between samples during the reading phase.
    READING_MODE_SAMPLES_INTERVAL = 0.5

    def __init__(
        self,
        NAME=None,
        R1=None,
        R2=None,
        MQ_ADC_PIN=None,
        RL_VALUE=None,
        RO_CLEAN_AIR=None,
        A_EXPO=None,
        M_EXPO=None,
        RSRO_CLEAN_AIR=None,
        MIN_CONCENTRATION=None,
        MAX_CONCENTRATION=None,
        MIN_HUMIDITY=None,
        MAX_HUMIDITY=None,
        MIN_TEMPERATURE=None,
        MAX_TEMPERATURE=None,
    ):
        """
        Creates a MQ sensor instance.
        """

        if NAME is None:
            raise ValueError("NAME value must be declared")
        if R1 is None:
            raise ValueError("R1 value must be declared")
        if R2 is None:
            raise ValueError("R2 value must be declared")
        if MQ_ADC_PIN is None:
            raise ValueError("MQ_ADC_PIN value must be declared")
        if RL_VALUE is None:
            raise ValueError("RL_VALUE value must be declared")
        if A_EXPO is None:
            raise ValueError("A_EXPO value must be declared")
        if M_EXPO is None:
            raise ValueError("M_EXPO value must be declared")
        if RSRO_CLEAN_AIR is None:
            raise ValueError("RSRO_CLEAN_AIR factor must be declared")
        if MIN_CONCENTRATION is None:
            raise ValueError("MIN_CONCENTRATION value must be declared")
        if MAX_CONCENTRATION is None:
            raise ValueError("MAX_CONCENTRATION value must be declared")
        if MIN_HUMIDITY is None:
            raise ValueError("MIN_HUMIDITY value must be declared")
        if MAX_HUMIDITY is None:
            raise ValueError("MAX_HUMIDITY value must be declared")
        if MIN_TEMPERATURE is None:
            raise ValueError("MIN_TEMPERATURE value must be declared")
        if MAX_TEMPERATURE is None:
            raise ValueError("MAX_TEMPERATURE value must be declared")

        if RO_CLEAN_AIR is None:
            print(
                "Sensor {0} RO_CLEAN_AIR value must be declared. Use calibrate_ro \
        to calculate Ro value in clean air.".format(
                    NAME
                )
            )
        else:
            print("Sensor {0} RO_CLEAN_AIR value declared.".format(NAME))

        #### CONCENTRATION CALCULATION ####
        # MQ gas sensor correlation function estimated from datasheet
        # http://davidegironi.blogspot.com/2017/05/mq-gas-sensor-correlation-function.html#.XdyM5R-YXKa
        # F(x) = (10^b)*(x^m) | gas_concentration = 10^b * (Rs/Ro)^m , R^2 = 0.999
        # ou seja: gas_concentration = a*x^m, x = Rs/Ro (Sensor current resistance divided by sensor resistance in clear air)
        # a = 10^b
        self.A_EXPO = A_EXPO
        # m - expoente
        self.M_EXPO = M_EXPO

        #### ADC ####
        self._adc = ADC(pin_adc=MQ_ADC_PIN)  # ADC channel (MCP3008)

        #### RASPBERRY VOLTAGE DIVIDER (from circuit values) ####
        self.R1 = R1  # 10kOhms
        self.R2 = R2  # 20kOhms

        #### MQSENSOR Sensor ####
        self.NAME = NAME  # MQ Sensor name/alias

        # Environment working conditions
        self.MIN_HUMIDITY = MIN_HUMIDITY
        self.MAX_HUMIDITY = MAX_HUMIDITY
        self.MIN_TEMPERATURE = MIN_TEMPERATURE
        self.MAX_TEMPERATURE = MAX_TEMPERATURE

        # Load resistance (RL) of 30KOhms (=Req=(R1+R2))
        self.RL_VALUE = RL_VALUE

        # RSRO_CLEAN_AIR = RS/RO in pure air
        self.RSRO_CLEAN_AIR = RSRO_CLEAN_AIR
        # obtained from datasheet using webplotdigitilizer

        # By the datasheet figure we have to select
        # the max and min gas concentration sensibility points.
        # minimum concentration sensibility of gas sensor
        self.MIN_CONCENTRATION = MIN_CONCENTRATION
        # maximum concentration sensibility of gas sensor
        self.MAX_CONCENTRATION = MAX_CONCENTRATION

        # RO_CLEAN_AIR = Gas sensor resistance in clean air
        self.RO_CLEAN_AIR = RO_CLEAN_AIR

    def _read_RS(self):
        """Calculates the MQ sensor resistance (RS).

        The MQ sensor internal resistance (RS) and the load resistor (RL) are in serial.
        The sensor’s resistance RS and RL forms a voltage divider. The output voltage on
        the signal pin can be read via ADC.
        Given a value of RL , VCC (Power Supply Voltage), and VOUT (output voltage),
        RS can be derived.
        Since the Raspberry does not support 5V in input pins, it is necessary to use
        a second voltage divider to lower the VOUT voltage range from 0 - 5V to
        the 0 - 3.3V supported voltage range (VPIN).
        The new voltage divider replaces the RL resistor with a equivalent resistance value.
        Below we have a simple circuit ilustration:
        For boards that input pins supports 5V inputs:

                    VOUT
                    |
        VCC/---RS---|---RL---/GND

        For Raspberry:

        VCC/---RS---<VOUT>---R1---<VPIN>---R2---/GND

        (RL ≡ R1 + R2)

        Parameters
        ----------
        raw_adc_output : float

          Analogic value read from adc, represents the voltage VPIN

        max_adc_resolution : int

          Max ADC resolution value (tipically an ADC of 10bits is used,so the
          resolution range is 0-1023, the max resolution is 1023).

        Returns
        -------
        RS : float
          The calculated sensor resistance
        """

        # Using the VPIN voltage value instead of the raw value from adc.
        # VPIN = (self._adc.read_raw_value() * self.VCC_PI_INPUT_MAX) / self._adc.read_adc_max_resolution()  # Convert the adc discrete value
        #                                                                                                    # to a voltage equivalent value
        # Check if VOUT is 0V (VOUT is derived from VPIN, so we are checking if VPIN is 0V.
        # In practice, VPIN should not be 0V).
        try:

            # The voltage will be in the 0 - 3.3V range
            VPIN = self._adc.read_voltage()
            VOUT = ((self.R1 + self.R2) / self.R2) * VPIN
            RS = (self.VCC / VOUT - 1.0) * self.RL_VALUE

            return RS

        except ZeroDivisionError:
            raise MQSensorException(
                "ZeroDivisionError: Failed to read MQ sensor, VPIN returned 0V, check wiring!"
            )
        except MQSensorException:
            raise MQSensorException(
                "Failed to read MQ sensor. Check wiring and parameter values!"
            )

    def calibrate_ro(self, current_humidity=None, current_temperature=None):
        """
        Returns to stdout the Ro value in clean air if the sensor is in working temperature and humidty range.
        Otherwise, returns None

        Assuming that the sensor is in clean air, the function uses the method _read_RS
        to get the gas sensor resistance (RS) in clean air, then it divides by RSRO_CLEAN_AIR value
        to obtain the RO_CLEAN_AIR value in clean air.

        """
        if current_humidity is None:
            raise ValueError("Humidity value must be informed")
        if current_temperature is None:
            raise ValueError("Temperature value must be informed")

        print("Calibrating  Sensor {0} Ro value in clean air...".format(self.NAME))
        # Check if MQ sensor is in valid environment working conditions
        if self._check_working_conditions(
            current_humidity=current_humidity, current_temperature=current_temperature
        ):

            rs = 0.0

            for i in range(self.CALIBRATION_SAMPLES):
                rs += self._read_RS()
                time.sleep(self.CALIBRATION_SAMPLES_INTERVAL)

            rs = rs / self.CALIBRATION_SAMPLES  # Calculate the readings average

            ro = rs / self.RSRO_CLEAN_AIR  # Calculate RO value in clean air
            # RS/RO = RSRO_CLEAN_AIR => RO = RS/RSRO_CLEAN_AIR
            # RSRO_CLEAN_AIR is obtained from the datasheet

            ro = round(ro, 3)

            print("Calibrating Ro in clean air...done!")
            print("{0} RO_CLEAN_AIR = {1}".format(self.NAME, ro))
        else:
            print("Calibrating Ro in clean air...failed!")
            print("{0} RO_CLEAN_AIR = {1}".format(self.NAME, None))
            print(
                "Sensor {0} is not in environment working conditions: Invalid temperature or humidity condition!".format(
                    self.NAME
                )
            )

    def _get_average_rs(self):
        """
        Returns the average gas sensor resistence (RS). The amount of samples to be used during the reading phase.
        is defined by the constant READING_MODE_SAMPLES.
        """

        rs = 0.0

        for i in range(self.READING_MODE_SAMPLES):
            rs += self._read_RS()
            time.sleep(self.READING_MODE_SAMPLES_INTERVAL)

        rs = rs / self.READING_MODE_SAMPLES  # Calculate the readings average

        return rs

    def calibrate(self):
        """
        The MQ sensors needs an warmup time before taking a reading, usually 30 minutes
        for these kind of sensors. It can be done once for all the connected
        sensors.
        """
        print(
            "Calibrating MQ sensor pre-heat time ({0} seconds)...".format(
                self.PREHEAT_TIME
            )
        )

        time.sleep(self.PREHEAT_TIME)

        print(
            "Calibrating MQ sensor pre-heat time ({0} seconds)... done!".format(
                self.PREHEAT_TIME
            )
        )

    def _check_temperature_range(self, current_temperature=None):
        """
        Returns True if current temperature is in the temperature working condition range of the MQ sensor.
        Otherwise, returns False.
        """
        if (
            current_temperature >= self.MIN_TEMPERATURE
            and current_temperature <= self.MAX_TEMPERATURE
        ):
            return True
        return False

    def _check_humidity_range(self, current_humidity=None):
        """
        Returns True if current humidity is in the humidity working condition range of the MQ sensor.
        Otherwise, returns False.
        """
        if (
            current_humidity >= self.MIN_HUMIDITY
            and current_humidity < self.MAX_HUMIDITY
        ):
            return True
        return False

    def _check_working_conditions(
        self, current_humidity=None, current_temperature=None
    ):
        """
        Return True if the MQ sensor is in environment working range. Otherwise, returns False.
        """
        if self._check_temperature_range(
            current_temperature
        ) and self._check_humidity_range(current_humidity):
            return True
        return False

    def _check_sensor_sensibility_range(self, gas_concentration=None):
        """
        Returns True if the gas concentration measured is in the sensibility range of the sensor.

        Otherwise, returns False.
        """
        if (
            gas_concentration >= self.MIN_CONCENTRATION
            and gas_concentration <= self.MAX_CONCENTRATION
        ):
            return True
        return False

    def _measure_current_gas_concentration(self):
        """
        Returns the actual gas concentration calculated/measured by the sensor.
        The value is rounded to 3 decimal digits.
        """
        if self.RO_CLEAN_AIR is None:
            raise ValueError(
                "Sensor {0} RO_CLEAN_AIR value must be declared. Use calibrate_ro \
                          to calculate Ro value in clean air.".format(
                    self.NAME
                )
            )

        # Get actual rs and rsro ratio
        rs = self._get_average_rs()
        ratio_rsro = rs / self.RO_CLEAN_AIR

        # Equation to obtain gas concentration => gas_concentration = a*x^m, x = Rs/Ro
        gas_concentration = self.A_EXPO * pow(ratio_rsro, self.M_EXPO)

        return round(gas_concentration, 3)

    def get_reading(self, current_humidity=None, current_temperature=None):
        """
        Returns the gas concentration measured. 

        Returns None, when:
          - The MQ sensor is not in valid environment working conditions.

          OR

          - The gas concentration is out of range of the sensor sensibility.

        Parameters
        ----------
        current_humidity: float
          Humidity in percentage.

        current_temperature: float
          Temperature in degrees Celsius.
        """
        # Check if parameters were informed
        if current_humidity is None:
            raise ValueError("Humidity value must be informed")
        if current_temperature is None:
            raise ValueError("Temperature value must be informed")

        # Check if MQ sensor is not in valid environment working conditions
        if not self._check_working_conditions(
            current_humidity=current_humidity, current_temperature=current_temperature
        ):
            return None

        # Get current gas value measured by the sensor
        gas_concentration = self._measure_current_gas_concentration()

        # Check if the gas concentration measured is in the sensibility range of the sensor.
        if self._check_sensor_sensibility_range(gas_concentration=gas_concentration):
            return gas_concentration
        else:
            return None
