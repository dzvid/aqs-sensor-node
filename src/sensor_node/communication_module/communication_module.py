from environs import Env

from .ibrdtn_daemon import IbrdtnDaemon, DaemonInstanceCreationError, DaemonConnectionRefusedError

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
            # Create IBRDTN daemon client
            self._dtn_client = IbrdtnDaemon()

        except (DaemonInstanceCreationError, DaemonConnectionRefusedError) as error:
            raise CommunicationModuleCreationError(
                'Failed to create a communication module instance: ', error)

    def send_dtn_message(self, message=None):
        """
        Send a Message over DTN.

        Returns True, if the message was sent to the IBRDTN daemon succesfully.
        Otherwise, returns False.

        Parameters
        ----------
            message : A Message object
        """
        return self._dtn_client.send_message(payload=message.payload, custody=message.custody)
