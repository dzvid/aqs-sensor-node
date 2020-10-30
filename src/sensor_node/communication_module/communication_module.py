from environs import Env

from .ibrdtn_daemon import (
    IbrdtnDaemon,
    DaemonConnectionError,
)

# Load enviroment variables
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
                self._dtn_client.send_message(
                    payload=message.payload, custody=message.custody
                )
                sent = True
            except DaemonConnectionError:
                try:
                    self._dtn_client.create_connection()
                except DaemonConnectionError as error:
                    raise CommunicationModuleException(
                        "Communication module: Unable to send message due to connection problems to IBRDTN, perhaps not running or crashed? \n",
                        error,
                    )

    def close_connections(self):
        self._dtn_client.close_connection()
