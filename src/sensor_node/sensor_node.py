import time
import json

import datetime
from environs import Env


from .sensing_module.sensing_module import (
    SensingModule,
    SensingModuleCreationError,
)
from .communication_module.communication_module import (
    CommunicationModule,
    CommunicationModuleCreationError,
)
from .message import Message


# Load enviroment variables
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
            # Load sensor node parameters
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

            # Create sensor node modules
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
        print("Initializating sensor node....")

        self.sensing_module.calibrate_sensors()

        print("Initializating sensor node....done!")

    def sensing_mode(self):
        """
        Get sensors readings from sensing module and send them to communicatio
        module.
        """
        print("Sensor node in sensing mode!")

        while True:
            current_reading = self.sensing_module.read_sensors()

            if current_reading is not None:
                message = self._generate_message(reading=current_reading)
                self.communication_module.send_message(message=message)

            self._wait_time_interval_next_reading()

    def _generate_message(self, reading=None):
        """
        Generates a message containing a reading to be sent over DTN.

        Parameters
        ----------
        reading : Reading
            A Reading object representing a sensors reading.

        Returns
        ---------
        A Message object containg a payload and a custody. 
        Payload has a JSON with two keys:
          sensor_node : sensor node uuid;
          reading : contains a reading collected from sensors.
        Custody: no custody transference is used.
        """

        payload = {
            "sensor_node": {"uuid": self._uuid},
            "reading": reading.to_dict(),
        }

        return Message(
            payload=json.dumps(payload),
            custody=env.bool("MESSAGE_CUSTODY", default=None),
            lifetime=env.int("MESSAGE_LIFETIME", default=None),
        )

    def _wait_time_interval_next_reading(self):
        """
        Delay execution for a fixed time interval before take a new sensor node
        reading.
        """
        time.sleep(self._reading_interval)
