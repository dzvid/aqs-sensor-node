# comments about connecting to the daemon API: https://mail.ibr.cs.tu-bs.de/pipermail/ibr-dtn/2014-January/000538.html
from struct import pack, unpack
import socket
import errno
import base64
import json
from json import JSONDecodeError


class IbrdtnDaemonException(Exception):

    pass


class IbrdtnDaemon():
    """
    Class to interface to the IBRDTN daemon API.
    """

    def __init__(self):
        try:
            # Address and port of the DTN daemon
            self._DAEMON_ADDRESS = 'localhost'
            self._DAEMON_PORT = 4550
            # Application message source, which will be concatenated with the DTN Endpoint identifier of the node
            # where this script actually runs
            self._APP_SOURCE = 'data_sender'
            # DTN Endpoint identifier of the destination application running on the node where the MQTT broker actually runs
            self._DESTINATION_EID = 'dtn://aqs.uea.edu.dtn/broker'

            # Create the socket to communicate with the DTN daemon
            self._daemon_socket = socket.socket()
            # Connect to the DTN daemon
            self._daemon_socket.connect(
                (self._DAEMON_ADDRESS, self._DAEMON_PORT))
            # Get a file object (stream) associated with the daemon's socket
            self._daemon_file_descriptor = self._daemon_socket.makefile()
            # Read daemon's header response
            self._daemon_file_descriptor.readline()
            # Switch into extended protocol mode
            self._daemon_socket.send(b"protocol extended\n")
            # Read protocol switch response
            self._daemon_file_descriptor.readline()
            # Set endpoint identifier
            self._daemon_socket.send(bytes("set endpoint %s\n" %
                                           self._APP_SOURCE, encoding="UTF-8"))
            # Read protocol set EID response
            self._daemon_file_descriptor.readline()
            # Read the full DTN Endpoint identifier of this application
            self._daemon_socket.send(b"registration list\n")
            # Read the header of registration list response
            self._daemon_file_descriptor.readline()
            # Read the full DTN Endpoint identifier of this application
            self._SOURCE_EID = self._daemon_file_descriptor.readline().rstrip()
            # Read the last empty line of the response
            self._daemon_file_descriptor.readline()

            # Now we have a listening endpoint from which we can send bundles
        except ConnectionRefusedError:
            raise ConnectionRefusedError(
                "Failed to create an instance.\nError while trying to connect to the IBRDTN daemon.\nIs IBRDTN daemon running?")

    def close_socket(self):
        """
        Closes the file descriptor (stream) and the socket open to interface to the IBTDTN daemon API.
        """
        # Close stream
        self._daemon_file_descriptor.close()
        # Close socket
        self._daemon_socket.close()

    # JSON payload message validation method
    def _is_json(self, payload):
        """
        Check if the payload message is a valid JSON string.

        Parameters
        ----------
            payload : expected JSON string
                The message payload to be send.
        """
        try:
            json_object = json.loads(payload)
        except JSONDecodeError as e:
            print(e)
        except ValueError as e:
            print(e)
            return False
        except TypeError as e:
            print(e)
            return False
        return True

    def create_bundle(self, payload_message=None, custody=None):
        """
        Returns a bundle containing the string JSON payload message.
        """
        # The bundle payload is a Base64 encoded string
        bundle = "Source: %s\n" % self._SOURCE_EID
        bundle += "Destination: %s\n" % self._DESTINATION_EID

        # Set bundle custody processing flag
        if custody == True:
            bundle += "Processing flags: 156\n"
        else:
            bundle += "Processing flags: 148\n"

        bundle += "Blocks: 1\n\n"
        bundle += "Block: 1\n"
        bundle += "Flags: LAST_BLOCK\n"
        bundle += "Length: %d\n\n" % len(
            bytes(payload_message, encoding="UTF-8"))
        bundle += "%s\n\n" % str(base64.b64encode(
            payload_message.encode(encoding="UTF-8")), encoding="UTF-8")

        return bundle

    def send_bundle_to_daemon(self, bundle=None):
        """
        Send a bundle to the IBRDTN daemon API.
        """

        try:
            self._daemon_socket.send(b"bundle put plain\n")
            self._daemon_file_descriptor.readline()

            self._daemon_socket.send(bytes(bundle, encoding="UTF-8"))
            self._daemon_file_descriptor.readline()

            self._daemon_socket.send(b"bundle send\n")
            self._daemon_file_descriptor.readline()

            print("Following message converted to bundle:\n")
            print("%s" % (bundle))
            print("Bundle sent!\n")
        except (ConnectionError, BrokenPipeError):
            print(
                "Connection problem to the DTN daemon, could not send the bundle!")

    def send_message(self, payload_message=None, custody=None):
        """
        Create a bundle from a payload message and send it through IBRDTN daemon.

        Parameters
        ----------
            payload_message : JSON 
                A payload message in JSON format that is gonna be the bundle payload.

            custody : Boolean
                Enables the custody processing flag. The bundle processing flags indicate
                if a bundle requires custody or not. DEFAULT VALUE is False.
                - Set to True, to indicate if a bundle requires custody.
                - Set to False, to indicate if a bundle DOES NOT requires custody.
        """
        # Check method parameters
        if payload_message is None:
            raise ValueError("payload message value can not be None.")
        if custody is None:
            raise ValueError("custody value can not be None.")

        # Check if payload is a valid json string, send the message
        if self._is_json(payload_message):
            # Build the bundle containing the payload message
            bundle = self.create_bundle(
                payload_message=payload_message, custody=custody)
            # Send the message to the IBRDTN daemon
            self.send_bundle_to_daemon(bundle=bundle)

        else:
            print("Invalid payload message. Payload message must be a JSON string!")
