from unittest import mock

from socket_listener.receivers import UDPSocketReceiver
from socket_listener.handlers import UDPRequestHandler
from socket_listener.sinks import GooglePubSub


def test_handle():
    data, socket = b"This is the data.", None
    request = (data, socket)
    address = ("123.99.100.80", 10110)

    receiver_mock = UDPSocketReceiver(sinks=[mock.Mock(spec=GooglePubSub)])
    handler = UDPRequestHandler(request, address, receiver_mock.server)
    handler.handle()
