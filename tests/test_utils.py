import pytest

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


def test_fails_with_invalid_lines():
    lines = [
        "garbage",  # invalid
        "!AIVDM,1,1,,A,single1,0",
    ]

    with pytest.raises(ValueError, match="Line with NMEA prefix not recognized"):
        list(chunked_nmea_it(lines))


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


def test_chunked_nmea_it_preserves_lines():
    # Sample input with different prefixes and both single and multipart messages
    input_lines = [
        r"\s:r1,t:test,c:1*00\!AIVDM,1,1,,A,test1,0*00",
        r"\s:r2,t:test,c:2*00\!ABVDM,2,1,1,B,test2-part1,0*00",
        r"\s:r2,t:test,c:2*00\!ABVDM,2,2,1,B,test2-part2,0*00",
        r"\s:r3,t:test,c:3*00\!BSVDO,1,1,,A,test3,0*00",
        r"\s:r4,t:test,c:4*00\!ANVDM,1,1,,B,test4,0*00",
        r"\s:r5,t:test,c:5*00\!AIVDO,2,1,2,A,test5-part1,0*00",
        r"\s:r5,t:test,c:5*00\!AIVDO,2,2,2,A,test5-part2,0*00",
    ]

    # Reconstruct the lines from the chunked output
    output_lines = [
        line for packet
        in chunked_nmea_it(input_lines, max_lines_per_packet=20) for line in packet]

    # Assert all original lines are present and in the same order
    assert output_lines == input_lines
