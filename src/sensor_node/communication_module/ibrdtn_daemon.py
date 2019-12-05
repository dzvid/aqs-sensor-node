# comments about connecting to the daemon API: https://mail.ibr.cs.tu-bs.de/pipermail/ibr-dtn/2014-January/000538.html
from struct import pack, unpack
import socket
import errno
import base64
import json


class IbrdtnDaemon():

    def __init__(self):

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
        self._daemon_socket.connect((self._DAEMON_ADDRESS, self._DAEMON_PORT))
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

    def close_socket(self):
        # Close stream
        self._daemon_file_descriptor.close()
        # Close socket
        self._daemon_socket.close()

    def send_bundle(self, message=None, custody=False):
        """
        Create a bundle from a message and send it through IBR-DTN deamon
        Parameters
        ----------
            message : JSON 
                A message in JSON format that is the bundle payload.

            custody : Boolean
                Enables the custody processing flag. The bundle processing flags indicate
                if a bundle requires custody or not. 
                Set to True to indicate if a bundle requires custody.
                Set to False indicate if a bundle DOES NOT requires custody.
        """
        message = json.dumps("{ message : 'Hello DTN!' }")
        payload = message
        print(payload, type(payload))

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
        bundle += "Length: %d\n\n" % len(bytes(payload, encoding="UTF-8"))
        bundle += "%s\n\n" % str(base64.b64encode(
            payload.encode(encoding="UTF-8")), encoding="UTF-8")

        self._daemon_socket.send(b"bundle put plain\n")
        self._daemon_file_descriptor.readline()

        self._daemon_socket.send(bytes(bundle, encoding="UTF-8"))
        self._daemon_file_descriptor.readline()

        self._daemon_socket.send(b"bundle send\n")
        self._daemon_file_descriptor.readline()

        print("Following message converted to bundle:\n")
        print("%s" % (bundle))
        print("Bundle sent\n")
