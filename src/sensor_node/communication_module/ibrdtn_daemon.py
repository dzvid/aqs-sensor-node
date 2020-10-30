# comments about connecting to the daemon API: https://mail.ibr.cs.tu-bs.de/pipermail/ibr-dtn/2014-January/000538.html
import socket
import base64

from time import sleep
from environs import Env


# Load enviroment variables
env = Env()
env.read_env()


class IbrdtnDaemonException(Exception):
    """
    Generic error occurs while interfacing with the IBRDTN daemon.
    """


# class DaemonInstanceCreationError(ValueError):
#     """
#     Failed to load parameters from enviroment variable (.env file).
#     """


class DaemonConnectionError(ConnectionError):
    """
    Connection problem when interacting with IBRDTN daemon API.
    """


# class DaemonBundleUploadError(IbrdtnDaemonException):
#     """
#     Unable to send bundles to the DTN Daemon. Check if the file descriptor
#     and socket are not closed or disconnected from the daemon.
#     """


# class DaemonMessageValueError(ValueError):
#     """
#     Invalid payload message value or invalid custody value.
#     Payload must be a JSON string. Custody must be a boolean value.
#     """


class IbrdtnDaemon:
    """
    Class to interface the communication with the IBRDTN daemon API.

    Attributes
    ----------
    address : String
        IBRDTN daemon address.

    port : int
        IBRDTN daemon port.

    app_source : String
        Application message source, which will be concatenated with the DTN
        Endpoint identifier of the node running this code.
    
    destination_eid : String
        DTN Endpoint identifier of the destination application running on
        destination node.

    Raises
    ------
    DaemonInstanceCreationError :
        An environment variable was not declared.

    """

    def __init__(
        self, address=None, port=None, app_source=None, destination_eid=None
    ):
        if address is None:
            raise ValueError("Daemon address must be informed.")
        if port is None:
            raise ValueError("Daemon port must be informed.")
        if app_source is None:
            raise ValueError("DTN app source must be informed.")
        if destination_eid is None:
            raise ValueError("DTN destination eid must be informed.")

        self._daemon_address = address
        self._daemon_port = port
        self._app_source = app_source
        self._destination_eid = destination_eid
        # Now we create a listening endpoint from which we can send bundles
        #  _dtn_source_eid: Full DTN Endpoint identifier of this application
        # (sensor eid + app source)
        # (the value is set below in _connect_to_daemon method)
        self._daemon_socket = None
        self._daemon_stream = None
        self._dtn_source_eid = None

    def create_connection(self):
        """
          Attempts to create connection to IBRDTN daemon 20 times, taking 30 seconds
          interval between each try.
          If connection is unsuccessful, throws a DaemonConnectionError exception.
          """
        self._daemon_socket = None
        self._daemon_stream = None
        self._dtn_source_eid = None

        connected = False
        current_try = 0
        max_tries = 20

        while not connected and current_try < max_tries:
            try:
                print(
                    "IBRDTNDaemon: Trying to connect to daemon, try n° {0}".format(
                        current_try + 1
                    )
                )
                self._connect_to_daemon()
                connected = True
            except ConnectionError:
                current_try += 1
                sleep(30)

        if not connected and current_try == max_tries:
            raise DaemonConnectionError(
                "Failed to create_connection to IBRDTN after {0} tries. Please, check IBRDTN daemon.".format(
                    max_tries
                )
            )

    def _connect_to_daemon(self):
        """
        Creates a socket and a stream (file object aka file descriptor)
        to communicate with DTN daemon. Sets the daemon in protocol extended
        mode and the endpoint app source, then gets the full DTN Endpoint
        identifier of this application.
        """
        try:
            # Create socket to communicate with the DTN daemon
            self._daemon_socket = socket.socket()
            # Connect to the DTN daemon
            self._daemon_socket.connect(
                (self._daemon_address, self._daemon_port)
            )
            # Get a file object (file descriptor/stream) associated with the
            # daemon's socket
            self._daemon_stream = self._daemon_socket.makefile()
            # Read daemon"s header response
            self._daemon_stream.readline()
            # Switch into extended protocol mode
            self._daemon_socket.send(b"protocol extended\n")
            # Read protocol switch response
            self._daemon_stream.readline()
            # Set endpoint identifier
            self._daemon_socket.send(
                bytes("set endpoint %s\n" % self._app_source, encoding="UTF-8",)
            )
            # Read protocol set EID response
            self._daemon_stream.readline()
            self._daemon_socket.send(b"registration list\n")
            # Read the header of registration list response
            self._daemon_stream.readline()
            # Read the full DTN Endpoint identifier of this application
            self._dtn_source_eid = self._daemon_stream.readline().rstrip()
            # Read the last empty line of the response
            self._daemon_stream.readline()
        except ConnectionError as error:
            raise ConnectionError(
                "Failed to create a socket and stream to the IBRDTN daemon.\n",
                error,
            )

    def close_connection(self):
        """
        Closes stream (file descriptor) and socket to IBTDTN daemon API.
        """
        self._dtn_source_eid = None
        if self._daemon_stream:
            self._daemon_stream.close()

        if self._daemon_socket:
            self._daemon_socket.close()

    def send_message(self, payload=None, custody=None):
        """
        Create a bundle from a JSON payload message
        and send it through IBRDTN daemon.
     
        Parameters
        ----------
            payload : JSON
                A JSON string that is gonna be bundle payload.
            custody : boolean
                Indicates if bundle custody is necessary.

        Raises
        ------
        DaemonConnectionError
            Invalid value passed as parameter.
        """
        try:
            if payload is None:
                raise ValueError("Payload must be a string.")
            if custody is None:
                raise ValueError("Custody must be a boolean.")

            self._send_bundle(
                bundle=self._create_bundle(payload=payload, custody=custody)
            )
            print("Sensor node: Message sent SUCCESSFULLY to the DTN daemon!")
        except ValueError as error:
            print("Message not sent: Invalid values provided. \n", error)
        except DaemonConnectionError as error:
            raise DaemonConnectionError("Failed to send dtn message. \n", error)

    def _create_bundle(self, payload=None, custody=None):
        """
        Returns a bundle containing the payload string.

        Parameters
        ----------
        payload : String
            The payload contains a string value (e.g: a JSON/XML string).

        custody : Boolean
            Enables the custody processing flag. The bundle processing flags
            indicates if a bundle requires custody or not.
            DEFAULT VALUE is None.
            - Set to True, to indicate if a bundle requires custody.
            - Set to False, to indicate if a bundle DOES NOT requires custody.
        """
        # The bundle payload is a Base64 encoded string
        bundle = "Source: %s\n" % self._dtn_source_eid
        bundle += "Destination: %s\n" % self._destination_eid

        # Set bundle custody processing flag
        if custody is True:
            bundle += "Processing flags: 156\n"
        else:
            bundle += "Processing flags: 148\n"

        bundle += "Blocks: 1\n\n"
        bundle += "Block: 1\n"
        bundle += "Flags: LAST_BLOCK\n"
        bundle += "Length: %d\n\n" % len(bytes(payload, encoding="UTF-8"))
        bundle += "%s\n\n" % str(
            base64.b64encode(payload.encode(encoding="UTF-8")),
            encoding="UTF-8",
        )

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
            raise DaemonConnectionError(
                "Could not send bundle! Try to connect to daemon again.\n",
                error,
            )
