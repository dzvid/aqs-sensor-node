import time
import datetime
import json


class Reading():
    """
    Class that represents a reading collected by the Sensing Module.
    """

    def __init__(self, carbon_monoxide, pm2_5, pm10, ozone, temperature, relative_humidity, pressure):
        self.carbon_monoxide = carbon_monoxide
        self.pm2_5 = pm2_5
        self.pm10 = pm10
        self.ozone = ozone
        self.temperature = temperature
        self.relative_humidity = relative_humidity
        self.pressure = pressure
        self.collected_at = self._register_collected_at_date()

    def _register_collected_at_date(self):
        """
        Returns the local datetime in ISO 8601 format with timezone 
        and no microsecond info. Output format: "%Y-%m-%dT%H:%M:%S%Timezone"
        """

        # Calculate the offset taking into account daylight saving time
        utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
        utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
        collected_at = datetime.datetime.now().replace(
            microsecond=0, tzinfo=datetime.timezone(offset=utc_offset)).isoformat()
        return collected_at

    def toJSON(self):
        """
        Returns reading in JSON format.
        """
        reading = {
            "carbon_monoxide": self.carbon_monoxide,
            "pm2_5": self.pm2_5,
            "pm10": self.pm10,
            "ozone": self.ozone,
            "temperature": self.temperature,
            "relative_humidity": self.relative_humidity,
            "pressure": self.pressure,
            "collected_at": self.collected_at,
        }

        return json.dumps(reading)
