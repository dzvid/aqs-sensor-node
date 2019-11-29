# -*- coding: utf-8 -*-

# Adapted from:
#   http://sandboxelectronics.com/?p=165
#   http://davidegironi.blogspot.com/2017/05/mq-gas-sensor-correlation-function.html#.XdyM5R-YXKa
import time

from .sensor import Sensor
from .adc import ADC

class MQSensor(Sensor):

  ######################### Hardware Related Macros #########################
  VCC = 5.0                           # Power supply value (in Volts)
  VCC_PI_INPUT_MAX = 3.3              # Raspberry maximum input volta (in Volts)

  ######################### Software Related Macros #########################
  # Defines the amount of samples to be used during the calibration phase.
  CALIBRATION_SAMPLES = 10
  # Sets the time interval (in seconds) between samples during the calibration phase.
  CALIBRATION_SAMPLES_INTERVAL = 0.5
  # Defines the amount of samples to be used during the reading phase.
  READING_MODE_SAMPLES = 5
  # Sets the time interval (in seconds) between samples during the reading phase.
  READING_MODE_SAMPLES_INTERVAL = 0.5

  def __init__(self, R1=None, R2=None, MQ_ADC_PIN=None, RL_VALUE=None, RO_CLEAN_AIR=None,
  A_EXPO=None,  M_EXPO=None, RSRO_CLEAN_AIR=None, MIN_CONCENTRATION=None, MAX_CONCENTRATION=None):
    """
    Creates a MQ sensor instance.
    """

    if(R1 is None):
      raise ValueError("R1 value must be declared")
    if(R2 is None):
      raise ValueError("R2 value must be declared")
    if(MQ_ADC_PIN is None):
      raise ValueError("MQ_ADC_PIN value must be declared")
    if(RL_VALUE is None):
      raise ValueError("RL_VALUE value must be declared")
    if(A_EXPO is None):
      raise ValueError("A_EXPO value must be declared")
    if(M_EXPO is None):
      raise ValueError("M_EXPO value must be declared")
    if(RSRO_CLEAN_AIR is None):
      raise ValueError("RSRO_CLEAN_AIR value must be declared")
    if(MIN_CONCENTRATION is None):
      raise ValueError("MIN_CONCENTRATION value must be declared")
    if(MAX_CONCENTRATION is None):
      raise ValueError("MAX_CONCENTRATION value must be declared")

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
    self.R1 = R1                       # 10kOhms
    self.R2 = R2                       # 20kOhms

    #### MQSENSOR Sensor ####
    # Load resistance (RL) of 30KOhms (=Req=(R1+R2))
    self.RL_VALUE = RL_VALUE

    self.RSRO_CLEAN_AIR = RSRO_CLEAN_AIR  # RSRO_CLEAN_AIR = RS/RO in pure air
                                          # obtained from datasheet using webplotdigitilizer

    if(RO_CLEAN_AIR is None):
      self.RO_CLEAN_AIR = self.calibrate()  # RO_CLEAN_AIR = Gas sensor resistance in clean air
    else:
      self.RO_CLEAN_AIR = RO_CLEAN_AIR

                                                         # By the datasheet figure we have to select 
                                                         # the max and min gas concentration sensibility points.
    self.MIN_CONCENTRATION = MIN_CONCENTRATION           # minimum concentration sensibility of gas sensor
    self.MAX_CONCENTRATION = MAX_CONCENTRATION           # maximum concentration sensibility of gas sensor

  
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
    # TODO: Check requirements for when VOUT is 0V
    VPIN = self._adc.read_voltage()                       # The voltage will be in the 0 - 3.3V range
    VOUT = ((self.R1 + self.R2) / self.R2) * VPIN
    RS = (self.VCC / VOUT - 1.0) * self.RL_VALUE

    return RS

  def calibrate(self):
    """
    Assuming that the sensor is in clean air, the function uses the method _read_RS
    to get the gas sensor resistance (RS) in clean air, then it divides by RSRO_CLEAN_AIR value
    to obtain the RO_CLEAN_AIR value in clean air.
    """
    print("RO_CLEAN_AIR not informed!\nCalibrating gas sensor...")
    rs = 0.0

    for i in range(self.CALIBRATION_SAMPLES):
        rs += self._read_RS()
        time.sleep(self.CALIBRATION_SAMPLES_INTERVAL)

    rs = rs / self.CALIBRATION_SAMPLES    # Calculate the readings average

    ro = rs / self.RSRO_CLEAN_AIR         # Calculate RO value in clean air
                                          # RS/RO = RSRO_CLEAN_AIR => RO = RS/RSRO_CLEAN_AIR
                                          # RSRO_CLEAN_AIR is obtained from the datasheet
    print("Calibrating gas sensor...done!")
    print("RO_CLEAN_AIR = {0}".format(ro))

    return ro

  def _get_average_rs(self):
    """
    Returns the average gas sensor resistence (RS). The amount of samples to be used during the reading phase.
    is defined by the constant READING_MODE_SAMPLES. 
    """

    rs = 0.0

    for i in range(self.READING_MODE_SAMPLES):
        rs += self._read_RS()
        time.sleep(self.READING_MODE_SAMPLES_INTERVAL)

    rs = rs/self.READING_MODE_SAMPLES         # Calculate the readings average

    return rs



  def get_reading(self):
    """
    Returns the gas concentration measured. Returns None when the gas concentration is out of range of the sensor sensibility.
    """
    # Get actual rs and rsro ratio
    rs = self._get_average_rs()
    ratio_rsro = rs / self.RO_CLEAN_AIR

    # Equation to obtain gas concentration => gas_concentration = a*x^m, x = Rs/Ro
    gas_concentration = (self.A_EXPO * pow(ratio_rsro, self.M_EXPO))

    if(gas_concentration >= self.MIN_CONCENTRATION and gas_concentration <= self.MAX_CONCENTRATION ):       
      return round(gas_concentration, 3)
    else:
      return None
