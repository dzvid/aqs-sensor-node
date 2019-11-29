from abc import ABC, abstractmethod


class Sensor(ABC):

    @abstractmethod
    def calibrate(self):
        """
        Calibrates the sensor if necessary.
        """
        pass

    @abstractmethod
    def get_reading(self):
        """
        Return the sensor measured value.
        """
        pass
