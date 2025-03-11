from unittest import mock

from socket_listener.packet import Packet
from socket_listener.sinks import GooglePubSub


def test_decoded_data():
    p1 = Packet(b"asd ")
    assert p1.decoded_data == "asd"

    p2 = Packet(b"123 \n 456")
    assert p2.decoded_data == "123 \n 456"

    assert p2.time > p1.time


def test_messages():
    p = Packet(b"123 \n 456")

    assert len(p.messages) == 2
    assert p.messages[0] == "123"
    assert p.messages[1] == "456"


def test_size():
    p = Packet(b"123 \n 456")
    assert len(p.messages) == p.size


def test_empty():
    p = Packet(b"123 \n 456")
    assert not p.empty


def test_address():
    host, port = "123.0.0.20", 10110
    p = Packet(b"123", host=host, port=port)

    assert p.address == f"{host}:{port}"


def test_log():
    host, port = "123.0.0.20", 10110
    p = Packet(b"123", host=host, port=port)
    p.log()

    p = Packet(b"", host=host, port=port)  # empty packet
    p.log()


def test_publish():
    sinks = [mock.Mock(spec=GooglePubSub)]
    p = Packet(b"123")
    p.publish(sinks)
