from socket_listener.packet import Packet


def test_messages_basic_split():
    p = Packet(b"123 \n 456")
    assert len(p.messages_list) == 2
    assert p.messages_list[0] == b"123"
    assert p.messages_list[1] == b"456"


def test_messages_custom_delimiter():
    p = Packet(b"abc|def|ghi", delimiter="|")
    assert p.messages_list == [b"abc", b"def", b"ghi"]


def test_messages_strip_and_empty_lines():
    p = Packet(b"\n\n  a  \n\n b \n\n")
    assert p.messages_list == [b"a", b"b"]


def test_messages_invalid_utf8_fallback():
    # Invalid UTF-8 sequence
    p = Packet(b"\xff\xff", decode_method="utf-8")
    assert p.messages_list == [b"\xff\xff"]


def test_metadata_content():
    protocol, source, host, delimiter = "UDP", "krasnodar", "10.33.44.50", "."
    p = Packet(b"", protocol=protocol, source_name=source, source_host=host, delimiter=delimiter)

    assert p.delimiter == delimiter
    assert p.metadata["protocol"] == protocol
    assert p.metadata["source_host"] == host
    assert p.metadata["source_name"] == source
    assert p.metadata["time"] == p.time.isoformat()


def test_size_matches_message_count():
    p = Packet(b"1\n2\n3")
    assert p.size == 3
    assert p.size == len(p.messages_list)


def test_empty_packet_detection():
    assert Packet(b"").empty is True
    assert Packet(b"\n\n").empty is False  # Contains split-able newlines
    assert Packet(b"content").empty is False


def test_debug_logs(caplog):
    p = Packet(b"hello\nworld")
    with caplog.at_level("DEBUG"):
        p.debug()

    assert "hello" in caplog.text
    assert "world" in caplog.text


def test_messages_preserve_encoding_utf16():
    original = "a\nb\nc".encode("utf-16")
    p = Packet(original, decode_method="utf-16")

    expected = [s.encode("utf-16") for s in ["a", "b", "c"]]
    assert p.messages_list == expected
