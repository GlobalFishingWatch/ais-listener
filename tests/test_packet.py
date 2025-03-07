from socket_listener.packet import Packet


def test_decoded_data():
    p1 = Packet(b"asd ")
    assert p1.decoded_data == "asd"

    p2 = Packet(b"123 \n 456")
    assert p2.decoded_data == "123 \n 456"

    assert p2.timestamp > p1.timestamp


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
