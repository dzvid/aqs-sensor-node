import time
import datetime


class Reading:
    """
    Class that represents a reading collected by the Sensing Module.
    """

    def __init__(
        self,
        pm25,
        pm10,
        temperature=None,
        relative_humidity=None,
        pressure=None,
    ):
        self.pm25 = pm25
        self.pm10 = pm10
        self.temperature = temperature
        self.relative_humidity = relative_humidity
        self.pressure = pressure
        self.collected_at = self._register_collected_at_date()

    def _register_collected_at_date(self):
        """
        Returns the local datetime in ISO 8601 format with timezone.
        and no microseconds info. Output format: "%Y-%m-%dT%H:%M:%S%Timezone"
        """
        collected_at = (
            datetime.datetime.now()
            .astimezone()
            .replace(microsecond=0)
            .isoformat()
        )

        return collected_at

    def to_dict(self):
        """
        Returns reading in a dict.
        """
        reading = {
            "pm25": self.pm25,
            "pm10": self.pm10,
            "temperature": self.temperature,
            "relative_humidity": self.relative_humidity,
            "pressure": self.pressure,
            "collected_at": self.collected_at,
        }

        return reading
