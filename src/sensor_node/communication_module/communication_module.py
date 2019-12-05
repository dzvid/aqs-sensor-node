<<<<<<< Updated upstream
from ibrdtn_daemon import IbrdtnDaemon

from ibrdtn_daemon import DaemonInstanceCreationError, DaemonConnectionRefusedError
=======
from environs import Env

from ibrdtn_daemon import IbrdtnDaemon, DaemonInstanceCreationError, DaemonConnectionRefusedError

# Load enviroment variables
env = Env()
env.read_env()
>>>>>>> Stashed changes


class ClientCreationError(Exception):
    """
    Failed to create a communication module instance.
    """


class CommunicationModule:

    def __init__(self):
        try:
            # Create IBRDTN daemon client
            self._dtn_client = IbrdtnDaemon()

            self._DTN_CLIENT_BUNDLE_DEFAULT_CUSTODY = env.bool(
                'DTN_CLIENT_BUNDLE_DEFAULT_CUSTODY', default=None)

            if self._DTN_CLIENT_BUNDLE_DEFAULT_CUSTODY is None:
                raise DaemonInstanceCreationError(
                    'DTN_CLIENT_BUNDLE_DEFAULT_CUSTODY value must be declared.')

        except (DaemonInstanceCreationError, DaemonConnectionRefusedError) as error:
            raise ClientCreationError(
                'Failed to create a communication module instance: ', error)

    def send_dtn_message(self, message=None):
        """
        Send a JSON string message over DTN.

        Returns True, if the message was sent to the IBRDTN daemon succesfully.

        Otherwise, returns False.

        Parameters
        ----------
            message : JSON string
        """
        return self._dtn_client.send_message(payload_message=message, custody=self._DTN_CLIENT_BUNDLE_DEFAULT_CUSTODY)
