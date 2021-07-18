import time
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

        started_at = (
            datetime.datetime.now()
            .astimezone()
            .replace(microsecond=0)
            .isoformat()
        )
        msg_sent = 0
        read_total_tries = 0
        read_success = 0
        read_failure = 0

        while True:
            read_total_tries += 1
            current_reading = self.sensing_module.read_sensors()

            if current_reading is not None:
                read_success += 1
                payload = self._generate_sensor_node_reading_payload(
                    reading=current_reading
                )
                message = self.communication_module.generate_message(
                    payload=payload
                )
                self.communication_module.send_message(message=message)
                msg_sent += 1
            else:
                read_failure += 1

            print("-------STATUS--------\n")
            print("Started at: {0}".format(started_at))
            print("Total readings tries: {0} \n".format(read_total_tries))
            print("Success reading: {0} \n".format(read_success))
            print("Failure reading: {0} \n".format(read_failure))
            print("Total messages sent over dtn: {0}\n".format(msg_sent))
            print("---------------------\n")

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
