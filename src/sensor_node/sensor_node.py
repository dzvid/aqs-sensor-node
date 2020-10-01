import time
import json

import datetime
from environs import Env

from sensing_module.sensing_module import SensingModule
from communication_module.communication_module import CommunicationModule

from sensing_module.sensing_module import SensingModuleCreationError
from communication_module.communication_module import CommunicationModuleCreationError

from message import Message


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
            self._SENSOR_NODE_UUID = env.str('SENSOR_NODE_UUID', default=None)
            self._SENSOR_NODE_READING_INTERVAL = env.int(
                'SENSOR_NODE_READING_INTERVAL', default=None)
            self._SENSOR_NODE_MQTT_DATA_TOPIC = env.str(
                'SENSOR_NODE_MQTT_DATA_TOPIC', default=None)

            if(self._SENSOR_NODE_UUID is None):
                raise ValueError(
                    'SENSOR_NODE_UUID value must be provided.')
            if(self._SENSOR_NODE_READING_INTERVAL is None):
                raise ValueError(
                    'SENSOR_NODE_READING_INTERVAL must be provided.')
            if(self._SENSOR_NODE_MQTT_DATA_TOPIC is None):
                raise ValueError(
                    'SENSOR_NODE_MQTT_DATA_TOPIC must be provided.')

            # Create sensor node modules
            self.sensing_module = SensingModule()
            self.communication_module = CommunicationModule()

        except (ValueError, CommunicationModuleCreationError, SensingModuleCreationError) as error:
            raise SensorNodeCreationError(
                'Failed to create a sensor node instance: ', error)

    def start_up(self):
        """
        Sensor node initialization.
        """
        print('Initializating sensor node....')

        self.sensing_module.calibrate_sensors()

        print('Initializating sensor node....done!')

    def sensing_mode(self):
        """
        Get sensors readings from sensing module and send them to communication module.
        """
        print("Sensor node in sensing mode!")

        while True:
            # Set initial reading value
            current_reading = None

            current_reading = self.sensing_module.read_sensors()

            if current_reading is not None:

                message = self._generate_message(
                    reading=current_reading)

                reading_sent = self.communication_module.send_dtn_message(
                    message=message)

                if(reading_sent):
                    print('Sensor node: Message sent SUCCESSFULLY to the DTN daemon!')
                else:
                    print('Sensor node: Message FAILED to be sent to the DTN daemon!')
            else:
                print('Sensor node: FAILED to get a reading from sensing module!')

            self._wait_interval_next_reading(
                reading_interval=self._SENSOR_NODE_READING_INTERVAL)

    def _generate_message(self, reading=None):
        """
        Generates a message to be sent over DTN.

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
            'sensor_node': self._SENSOR_NODE_UUID,
            'reading': reading.toJSON()
        }

        return Message(payload=payload)

    def _wait_interval_next_reading(self, reading_interval=None):
        '''
        Delay execution for a fixed time interval before take a new sensor node reading.
        Args: reading_interval Time interval in seconds to wait until next reading.
        '''
        time.sleep(reading_interval)
