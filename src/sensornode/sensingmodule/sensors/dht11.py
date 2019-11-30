import board
import adafruit_dht


class DHT11Sensor:

    def __init__(self):
        self._dht = adafruit_dht.DHT11(board.D4)

    def get_humidity(self):
        """
        Returns the humidity value measured by the DHT11 sensor.

        In most cases you'll always get back a temperature or humidity value when requested, 
        but sometimes if there's electrical noise or the signal was interrupted in some way 
        you might see an exception thrown to try again.  It's normal for these sensors to 
        sometimes be hard to read and you might need to make your code retry a few times if 
        it fails to read (recommended to retry after 1/2 seconds). 
        Reading the sensor may rise an exception if a problem occurs, it catchs a
        RuntimeError. When the sensor trhws the exception, the method returns None. 
        """
        try:
            humidity = self._dht.humidity

            return humidity
        except RuntimeError as error:
            print(
                "Reading from DHT failure: {0}. Trying again!".format(error.args))
            return None
