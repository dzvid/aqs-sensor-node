import json


class Message:
    """
    A class that represents a message sent over DTN. A message has two attributes
      payload: A JSON string to be sent over the network;
      custody: A boolean flag indicating if DTN custody will be used. 
        By default, custody is False. Set to True to enable it for a message.
    """

    def __init__(self, payload=None, custody=False):
        self.payload = payload
        self.custody = custody

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
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, value):
        if not self._is_json(str_json=value):
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
