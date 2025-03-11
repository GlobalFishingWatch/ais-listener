from unittest import mock

from socket_listener.handlers import UDPRequestHandler
from socket_listener.sinks import GooglePubSub


class ServerMock:
    source_name = "Unknown"
    sinks = []


def test_handle():
    data = b"This is the data."
    socket = None
    host = "123.99.100.80"
    port = 10110

    request = (data, socket)
    address = (host, port)

    server = ServerMock()
    server.sinks = [mock.Mock(spec=GooglePubSub)]
    handler = UDPRequestHandler(request, address, server)
    handler.handle()
