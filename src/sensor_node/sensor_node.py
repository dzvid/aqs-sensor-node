import time

from environs import Env


from .sensing_module.sensing_module import (
    SensingModule,
    SensingModuleCreationError,
)
from .communication_module.communication_module import (
    CommunicationModule,
    CommunicationModuleCreationError,
)


# Load environment variables
env = Env()
env.read_env()


class SensorNodeException(Exception):
    """
    Generic sensor node error.
    """


class SensorNodeCreationError(SensorNodeException):
    """
    Failed to create sensor node.
    """


class SensorNode:
    """
    Class that represents a Sensor Node.
    """

    def __init__(self):
        try:
            self._uuid = env.str("SENSOR_NODE_UUID", default=None)
            self._reading_interval = env.int(
                "SENSOR_NODE_READING_INTERVAL", default=None
            )

            if self._uuid is None:
                raise ValueError("SENSOR_NODE_UUID value must be provided.")
            if self._reading_interval is None:
                raise ValueError(
                    "SENSOR_NODE_READING_INTERVAL must be provided."
                )

            self.sensing_module = SensingModule()
            self.communication_module = CommunicationModule()

        except (
            ValueError,
            CommunicationModuleCreationError,
            SensingModuleCreationError,
        ) as error:
            raise SensorNodeCreationError(
                "Failed to create a sensor node instance.\n", error
            )

    def startup(self):
        """
        Sensor node initialization.
        """
        print("Initializing sensor node....")

        self.sensing_module.calibrate_sensors()

        print("Initializing sensor node....done!")

    def sensing_mode(self):
        """
        Get sensors readings from sensing module and send them to communication
        module.
        """
        print("Sensor node in sensing mode!")

        while True:
            current_reading = self.sensing_module.read_sensors()

            if current_reading is not None:
                payload = self._generate_sensor_node_reading_payload(
                    reading=current_reading
                )
                message = self.communication_module.generate_message(
                    payload=payload
                )
                self.communication_module.send_message(message=message)

            self._wait_time_interval_next_reading()

    def _generate_sensor_node_reading_payload(self, reading=None):
        """
        Generates a payload containing a reading to be sent
        in a message over dtn.

        Parameters
        ----------
        reading : JSON
            A Reading object representing a sensors node reading.

        Returns
        ---------
        A payload JSON.
      """

        payload = {
            "sensor_node": {"id": self._uuid},
            "reading": reading.to_dict(),
        }

        return payload

    def _wait_time_interval_next_reading(self):
        """
        Delay execution for a fixed time interval before take a new sensor node
        reading.
        """
        time.sleep(self._reading_interval)
