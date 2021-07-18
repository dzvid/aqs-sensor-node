import json

from environs import Env
from .ibrdtn_daemon import (
    IbrdtnDaemon,
    DaemonConnectionError,
)
from .message import Message

env = Env()
env.read_env()


class CommunicationModuleException(Exception):
    """
    Generic Communication Module error.
    """


class CommunicationModuleCreationError(CommunicationModuleException):
    """
    Failed to create a Communication Module instance.
    """


class CommunicationModule:
    def __init__(self):
        try:

            self._address = env.str("DTN_DAEMON_ADDRESS", default=None)
            self._port = env.int("DTN_DAEMON_PORT", default=None)
            self._app_source = env.str("DTN_SENSOR_APP_SOURCE", default=None)
            self._destination_eid = env.str("DTN_DESTINATION_EID", default=None)

            self._dtn_client = IbrdtnDaemon(
                address=self._address,
                port=self._port,
                app_source=self._app_source,
                destination_eid=self._destination_eid,
            )

            self._dtn_client.create_connection()

        except (ValueError, DaemonConnectionError) as error:
            raise CommunicationModuleCreationError(
                "Failed to create a communication module instance: ", error
            )

    def send_message(self, message=None):
        """
        Sends a message over DTN.

        Parameters
        ----------
            message : A Message object

        Raises
        ------
            CommunicationModuleException
                Exception raised when module fails to connect to IBRDTN daemon.
        """
        sent = False
        while not sent:
            try:
                self._dtn_client.send_message(message)
                sent = True
            except DaemonConnectionError:
                try:
                    self._dtn_client.create_connection()
                except DaemonConnectionError as error:
                    raise CommunicationModuleException(
                        "Communication module: Unable to send message due to \
                          a connection problem to IBRDTN daemon, perhaps not \
                          running or crashed? \n",
                        error,
                    )

    def generate_message(self, payload=None):
        """
        Generates a message containing a payload to be sent over DTN.

        Parameters
        ----------
        payload : JSON
            Payload must be a JSON.

        Returns
        ---------
        A Message object containing following keys: a payload, a custody and
        a message's lifetime.
          - Payload: Contains data to be sent in JSON format.
          - Custody: Message custody, defaults to no custody transference.
          - Lifetime: Message's lifetime, defaults to a week (604800 seconds).
        """

        return Message(
            payload=json.dumps(payload),
            custody=env.bool("MESSAGE_CUSTODY", default=None),
            lifetime=env.int("MESSAGE_LIFETIME", default=604800),
        )

    def close_connections(self):
        self._dtn_client.close_connection()
