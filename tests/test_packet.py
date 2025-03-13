from socket_listener.packet import Packet


def test_messages():
    p = Packet(b"123 \n 456")

    assert len(p.messages_list) == 2
    assert list(p.messages_list)[0] == "123"
    assert list(p.messages_list)[1] == "456"


def test_metadata():
    protocol, source, host, delimiter = "UDP", "krasnodar", "10.33.44.50", "."
    p = Packet(b"", protocol=protocol, source_name=source, source_host=host, delimiter=delimiter)
    assert p.delimiter == "."

    assert p.metadata["protocol"] == protocol
    assert p.metadata["source_host"] == host
    assert p.metadata["source_name"] == source
    assert p.metadata["time"] == p.time.isoformat()


def test_size():
    p = Packet(b"123 \n 456")
    assert len(p.messages_list) == p.size


def test_empty():
    p = Packet(b"123 \n 456")
    assert not p.empty
