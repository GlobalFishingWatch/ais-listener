import logging
import pytest
from unittest import mock

from socket_listener.receivers import UDPSocketReceiver
from socket_listener.handlers import UDPRequestHandler
from socket_listener.sinks import GooglePubSub
from socket_listener.sinks.base import SinkError
from socket_listener.packet import Packet


@pytest.fixture
def test_address():
    return ("123.99.100.80", 10110)


@pytest.fixture
def test_data():
    return b"This is the data."


def test_udp_handler_publishes_packet(test_data, test_address, caplog):
    # Create a mock sink and spy on its publish method
    mock_sink = mock.Mock(spec=GooglePubSub)
    receiver = UDPSocketReceiver(sinks=[mock_sink], port=0)
    receiver.server.provider_name = "TestSource"
    receiver.server.delimiter = "\n"

    # Patch logging level to DEBUG to test debug messages.
    caplog.set_level(logging.DEBUG)

    # Instantiate handler and call handle
    handler = UDPRequestHandler((test_data, None), test_address, receiver.server)
    assert handler.server is receiver.server

    packet = mock_sink.publish.call_args[0][0]
    assert isinstance(packet, Packet)

    # Validate packet content
    assert packet.size == 1  # Only one message expected
    assert packet.data == test_data
    assert packet.protocol == "UDP"
    assert packet.source_host == test_address[0]
    assert packet.source_name == "TestSource"
    assert packet.delimiter == "\n"

    # Check logging output (INFO and DEBUG)
    assert any("Received" in msg for msg in caplog.messages)
    # assert any(test_data.decode(packet.decode_method) in msg for msg in caplog.messages)

    # Ensure the sink's publish method was called once with a Packet
    assert mock_sink.publish.call_count == 1


def test_udp_handler_unknown_source(test_data, test_address):
    mock_sink = mock.Mock(spec=GooglePubSub)
    receiver = UDPSocketReceiver(sinks=[mock_sink], port=0)
    receiver.server.delimiter = "\n"

    handler = UDPRequestHandler((test_data, None), test_address, receiver.server)
    handler.handle()

    packet = mock_sink.publish.call_args[0][0]
    assert packet.source_name == "Unknown"


def test_udp_handler_sinkerror_is_captured(test_data, test_address):
    class FailingSink:
        def publish(self, packet):
            raise SinkError("Sink failed")

    failing_sink = FailingSink()
    receiver = UDPSocketReceiver(sinks=[failing_sink], port=0)
    receiver.server.provider_name = "TestSource"
    receiver.server.delimiter = "\n"

    # Ensure exceptions dict is empty before
    assert not receiver.server.exceptions

    handler = UDPRequestHandler((test_data, None), test_address, receiver.server)
    handler.handle()

    # Confirm that the SinkError was caught and stored in the server's exceptions
    assert SinkError in receiver.server.exceptions
    exc = receiver.server.exceptions[SinkError]
    assert isinstance(exc, SinkError)
    assert "Sink failed" in str(exc)
