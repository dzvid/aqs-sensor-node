import json

from environs import Env

env = Env()
env.read_env()


class Message:
    """
    A class that represents a message sent over DTN.

    A message has following attributes:
    
      payload (String): A JSON string to be sent over the network;

      custody (Boolean): A boolean flag indicating if DTN custody will be used.
        By default, custody is False. Set to True to enable it for a message;

      lifetime (int): Message lifetime in seconds;
    """

    def __init__(self, payload=None, custody=False, lifetime=None):
        self.payload = payload
        self.custody = custody
        self.lifetime = lifetime

    @property
    def custody(self):
        return self._custody

    @custody.setter
    def custody(self, value):
        self._custody = value

    @custody.getter
    def custody(self):
        return self._custody

    @property
    def lifetime(self):
        return self._lifetime

    @lifetime.setter
    def lifetime(self, value):
        if not isinstance(value, int):
            raise ValueError("Lifetime must be an integer")
        self._lifetime = value

    @lifetime.getter
    def lifetime(self):
        return self._lifetime

    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, value):
        if not self._is_json(str_json=value) or value is None:
            raise ValueError("Payload must be a JSON string")
        self._payload = value

    @payload.getter
    def payload(self):
        return self._payload

    def _is_json(self, str_json):
        try:
            json.loads(str_json)
        except ValueError:
            return False
        return True
