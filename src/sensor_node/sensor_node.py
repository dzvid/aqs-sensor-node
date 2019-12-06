import time
import json

import datetime
from environs import Env

from sensing_module.sensing_module import SensingModule
from communication_module.communication_module import CommunicationModule

from sensing_module.sensing_module import SensingModuleCreationError
from communication_module.communication_module import CommunicationModuleCreationError


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
            self._SENSOR_NODE_READING_INTERVAL = env.str(
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

    def begin(self):
        """
        Sensor node initialization.
        """
        print('Initializating sensor node....')

        self.sensing_module.calibrate_sensors()

        print('Initializating sensor node....done!')

    def sensing_mode(self):
        """
        Sensor node sensing mode: collects readings and send them to the server.
        """
        print("Sensor node in sensing mode!")

        while True:
            # Set initial reading value
            current_reading = None

            current_reading = self.sensing_module.read_sensors()

            if current_reading is not None:

                json_payload_message = self._generate_message(
                    reading=current_reading)

                reading_sent = self.communication_module.send_dtn_message(
                    message=json_payload_message)

                if(reading_sent):
                    print('Sensor node: Message sent SUCCESSFULLY to the DTN daemon!')
                else:
                    print('Sensor node: Message FAILED to be sent to the DTN daemon!')
            else:
                print('Sensor node: FAILED to read the sensors')

            self._wait_interval_next_reading(
                self._SENSOR_NODE_READING_INTERVAL)

    def _generate_message(self, reading=None):
        """
        Returns a JSON string containing the sensor reading collected.

        The JSON has two keys:
          - topic: string topic to publish the sensor reading.

          - payload: json containing the sensor node information and 
                  the values read from the sensors.

        Parameters
        ----------
        reading : dict
            A dictionary containing the sensor measured values. 
        """
        reading['uuid'] = self._SENSOR_NODE_UUID
        reading['collected_at'] = self._get_current_datetime()

        payload_message = dict()
        payload_message['topic'] = self._SENSOR_NODE_MQTT_DATA_TOPIC
        payload_message['payload'] = reading

        return json.dumps(payload_message)

    def _get_current_datetime(self):
        """
        Returns the local datetime in ISO 8601 format with timezone 
        and no microsecond info.
        Output format: "%Y-%m-%dT%H:%M:%S%Timezone"
        """

       # Calculate the offset taking into account daylight saving time
        utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
        utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
        collected_at = datetime.datetime.now().replace(
            microsecond=0, tzinfo=datetime.timezone(offset=utc_offset)).isoformat()
        return collected_at

    def _wait_interval_next_reading(self, reading_interval=None):
        '''
        Delay execution for a fixed time interval before take a new sensor node reading.
        Args: reading_interval Time interval in seconds to wait until next reading.
        '''
        time.sleep(reading_interval)
