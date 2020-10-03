# comments about connecting to the daemon API: https://mail.ibr.cs.tu-bs.de/pipermail/ibr-dtn/2014-January/000538.html
import socket
import errno
import base64
import json

from struct import pack, unpack
from environs import Env
from json import JSONDecodeError


# Load enviroment variables
env = Env()
env.read_env()


class IbrdtnDaemonException(Exception):
    """
    Generic error occurs while interfacing with the IBRDTN daemon.
    """


class DaemonInstanceCreationError(ValueError):
    """
    Failed to load parameters from enviroment variable (.env file).
    """


class DaemonConnectionRefusedError(IbrdtnDaemonException):
    """
    Unable to connect to the IBRDTN daemon API. Is the program running?
    """


class DaemonBundleUploadError(IbrdtnDaemonException):
    """
    Unable to send bundles to the DTN Daemon. Check if the file descriptor
    and socket are not closed or disconnected from the daemon.
    """


class DaemonMessageValueError(ValueError):
    """
    Invalid payload message value or invalid custody value. 
    Payload must be a JSON string. Custody must be a boolean value.
    """


class IbrdtnDaemon():
    """
    Class to interface the communication with the IBRDTN daemon API.
    """

    def __init__(self):
        # Address and port of the DTN daemon
        self._DTN_DAEMON_ADDRESS = env.str(
            "DTN_DAEMON_ADDRESS", default=None)
        self._DTN_DAEMON_PORT = env.int("DTN_DAEMON_PORT", default=None)

        # Application message source, which will be concatenated with the DTN Endpoint identifier of the node
        # where this script actually runs
        self._DTN_APP_SOURCE = env.str(
            "DTN_SENSOR_APP_SOURCE", default=None)

        # DTN Endpoint identifier of the destination application running on the node where the MQTT broker actually runs
        self._DTN_DESTINATION_EID = env.str(
            "DTN_DESTINATION_EID", default=None)

        # Full DTN Endpoint identifier of this application(sensor eid + app source)
        # (the value is set below in _create_socket_and_stream method)
        self._DTN_SOURCE_EID = None

        if(self._DTN_DAEMON_ADDRESS is None):
            raise DaemonInstanceCreationError(
                "Failed to create an instance. DTN_DAEMON_ADDRESS must be informed.")
        if(self._DTN_DAEMON_PORT is None):
            raise DaemonInstanceCreationError(
                "Failed to create an instance. DTN_DAEMON_PORT must be informed.")
        if(self._DTN_APP_SOURCE is None):
            raise DaemonInstanceCreationError(
                "Failed to create an instance. DTN_APP_SOURCE must be informed.")
        if(self._DTN_DESTINATION_EID is None):
            raise DaemonInstanceCreationError(
                "Failed to create an instance. DTN_DESTINATION_EID must be informed.")

        # Now we create a listening endpoint from which we can send bundles
        self._daemon_socket = None  # Socket is created in _create_socket_and_stream()
        self._daemon_stream = None  # Stream is created in _create_socket_and_stream()
        self._create_socket_and_stream()

    def _create_socket_and_stream(self):
        """
        Creates the socket and stream (file object aka file descriptor) to communicate with the DTN daemon.
        """
        try:
            # Create the socket to communicate with the DTN daemon
            self._daemon_socket = socket.socket()
            # Connect to the DTN daemon
            self._daemon_socket.connect(
                (self._DTN_DAEMON_ADDRESS, self._DTN_DAEMON_PORT))
            # Get a file object (file descriptor/stream) associated with the daemon"s socket
            self._daemon_stream = self._daemon_socket.makefile()
            # Read daemon"s header response
            self._daemon_stream.readline()
            # Switch into extended protocol mode
            self._daemon_socket.send(b"protocol extended\n")
            # Read protocol switch response
            self._daemon_stream.readline()
            # Set endpoint identifier
            self._daemon_socket.send(bytes("set endpoint %s\n" %
                                           self._DTN_APP_SOURCE, encoding="UTF-8"))
            # Read protocol set EID response
            self._daemon_stream.readline()
            # Read the full DTN Endpoint identifier of this application
            self._daemon_socket.send(b"registration list\n")
            # Read the header of registration list response
            self._daemon_stream.readline()
            # Read the full DTN Endpoint identifier of this application
            self._DTN_SOURCE_EID = self._daemon_stream.readline().rstrip()
            # Read the last empty line of the response
            self._daemon_stream.readline()
        except ConnectionRefusedError as error:
            raise DaemonConnectionRefusedError(
                "Failed to create an instance.\n \
                Error while trying to socket to the IBRDTN daemon.\n \
                Is IBRDTN daemon running?", error)

    def close_socket_and_stream(self):
        """
        Closes the stream (file descriptor) and the socket open to interface to the IBTDTN daemon API.
        """
        # Close stream
        self._daemon_stream.close()
        # Close socket
        self._daemon_socket.close()

    def _create_bundle(self, payload=None, custody=None):
        """
        Returns a bundle containing the payload string.

        Parameters
        ----------
        payload : String 
            The payload contains a string value, it can be anything (e.g: a JSON/XML string).

        custody : Boolean
                Enables the custody processing flag. The bundle processing flags indicate
                if a bundle requires custody or not. DEFAULT VALUE is None.
                - Set to True, to indicate if a bundle requires custody.
                - Set to False, to indicate if a bundle DOES NOT requires custody.
        """
        # The bundle payload is a Base64 encoded string
        bundle = "Source: %s\n" % self._DTN_SOURCE_EID
        bundle += "Destination: %s\n" % self._DTN_DESTINATION_EID

        # Set bundle custody processing flag
        if custody == True:
            bundle += "Processing flags: 156\n"
        else:
            bundle += "Processing flags: 148\n"

        bundle += "Blocks: 1\n\n"
        bundle += "Block: 1\n"
        bundle += "Flags: LAST_BLOCK\n"
        bundle += "Length: %d\n\n" % len(
            bytes(payload, encoding="UTF-8"))
        bundle += "%s\n\n" % str(base64.b64encode(
            payload.encode(encoding="UTF-8")), encoding="UTF-8")

        return bundle

    def _send_bundle(self, bundle=None):
        """
        Send a bundle to the IBRDTN daemon API.

        Parameters
        ----------
        bundle : String 
            A DTN bundle to be sent. It is formatted according to the format
            accepted by the IBRDTN daemon API.
        """

        try:
            self._daemon_socket.send(b"bundle put plain\n")
            self._daemon_stream.readline()

            self._daemon_socket.send(bytes(bundle, encoding="UTF-8"))
            self._daemon_stream.readline()

            self._daemon_socket.send(b"bundle send\n")
            self._daemon_stream.readline()

            print("Following message converted to bundle:\n")
            print("%s" % (bundle))
            print("Bundle sent!\n")

        except (ConnectionError, BrokenPipeError) as error:
            raise DaemonBundleUploadError(
                "Connection problem to the DTN daemon, could not send the bundle!", error)

    def send_message(self, payload=None, custody=None):
        """
        Create a bundle from a JSON payload message and send it through IBRDTN daemon.

        Returns True, if the message was sent to the IBRDTN daemon succesfully.

        Otherwise, returns False.

        Parameters
        ----------
            payload : JSON 
                A string in JSON format that is gonna be the bundle payload.


        """
        try:

            if payload is None:
                raise DaemonMessageValueError(
                    "Payload message value can not be None, payload message must be a string.")
            if custody is None:
                raise DaemonMessageValueError(
                    "Custody value can not be None, custody must a boolean value.")

            self._send_bundle(bundle=self._create_bundle(
                payload=payload, custody=custody))

            return True
        except (DaemonMessageValueError, DaemonBundleUploadError) as error:
            print("Failed to send dtn message: ", error)
            return False
