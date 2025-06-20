from socket_listener.utils import chunked_nmea_it


def test_single_part_sentences_split_correctly():
    lines = [f"!AIVDM,1,1,,A,data{i},0" for i in range(45)]
    packets = list(chunked_nmea_it(lines, max_lines_per_packet=20))

    assert len(packets) == 3
    assert all(len(p) <= 20 for p in packets)
    assert sum(len(p) for p in packets) == 45


def test_multipart_not_split():
    lines = [
        "!AIVDM,2,1,abc,A,part1,0",
        "!AIVDM,2,2,abc,A,part2,0",
        "!AIVDM,1,1,,A,single1,0",
        "!AIVDM,2,1,def,A,part3,0",
        "!AIVDM,2,2,def,A,part4,0"
    ]
    packets = list(chunked_nmea_it(lines, max_lines_per_packet=3))

    assert len(packets) == 2
    assert packets[0] == [
        "!AIVDM,2,1,abc,A,part1,0",
        "!AIVDM,2,2,abc,A,part2,0",
        "!AIVDM,1,1,,A,single1,0"
    ]
    assert packets[1] == [
        "!AIVDM,2,1,def,A,part3,0",
        "!AIVDM,2,2,def,A,part4,0"
    ]


def test_partial_multipart_at_end_is_flushed():
    lines = [
        "!AIVDM,2,1,xyz,A,part1,0",
        "!AIVDM,1,1,,A,single,0",
        "!AIVDM,2,2,xyz,A,part2,0",
    ]
    packets = list(chunked_nmea_it(lines, max_lines_per_packet=2))

    assert len(packets) == 2
    assert packets[0] == ["!AIVDM,2,1,xyz,A,part1,0", "!AIVDM,1,1,,A,single,0"]
    assert packets[1] == ["!AIVDM,2,2,xyz,A,part2,0"]


def test_ignores_empty_and_invalid_lines():
    lines = [
        "  ",  # empty
        "garbage",  # invalid
        "!AIVDM,1,1,,A,single1,0",
        "more garbage",
        "!AIVDM,1,1,,A,single2,0",
    ]
    packets = list(chunked_nmea_it(lines, max_lines_per_packet=2))

    assert len(packets) == 1
    assert packets[0] == [
        "!AIVDM,1,1,,A,single1,0",
        "!AIVDM,1,1,,A,single2,0"
    ]


def test_multiple_multipart_sequences_in_one_packet():
    lines = [
        "!AIVDM,2,1,abc,A,part1,0",
        "!AIVDM,2,2,abc,A,part2,0",
        "!AIVDM,2,1,def,A,part3,0",
        "!AIVDM,2,2,def,A,part4,0",
    ]
    packets = list(chunked_nmea_it(lines, max_lines_per_packet=10))
    assert len(packets) == 1
    assert packets[0] == lines
