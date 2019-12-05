from ibrdtn_daemon import IbrdtnDaemon

from ibrdtn_daemon import DaemonInstanceCreationError, DaemonConnectionRefusedError


class ClientCreationError(Exception):
    """
    Failed to create a communication module instance.
    """


class CommunicationModule:

    def __init__(self):
        try:
            # Create IBRDTN daemon client
            self._dtn_client = IbrdtnDaemon()
            self._DTN_CLIENT_BUNDLE_DEFAULT_CUSTODY = False
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
