import pytest
from util.nmea import format_nmea

source_port_map = {
    0: 'ais-listener',
    1: 'source1'
}


@pytest.mark.parametrize("source,message,addr,timestamp,port,expected", [
    ('source', 'message', '127.0.0.1', 123, 0,
        '\\t:source,s:127.0.0.1,c:123*58\\message'),
    ('source', 'message\n', '127.0.0.1', 123, 0,
        '\\t:source,s:127.0.0.1,c:123*58\\message'),
    ('source', '!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F', '127.0.0.1', 123, 0,
        '\\t:source,s:127.0.0.1,c:123*58\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F'),
    ('source', '\\t:other\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F', '127.0.0.1', 123, 1,
        '\\t:source,c:123,s:127.0.0.1*58\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F'),
    ('source', '\\t:other,s:station\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F', '127.0.0.1', 123, 1,
        '\\t:source,s:station,c:123*09\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F'),
    ('source', '\\t:other,c:999,s:station\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F', '127.0.0.1', 123, 1,
        '\\t:source,c:999,s:station*00\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F'),
    ('source', '\\c:bad_value\\message', '127.0.0.1', 123, 0,
        '\\c:bad_value\\message'),
    ('source', '\\s:rMT5858,*0E\\!AIVDM,1,1,,A,13SeLS7P1j15l@FHcA<PM?vN05`P,0*26', '127.0.0.1', 123, 1,
        '\\s:rMT5858,t:source,c:123*18\\!AIVDM,1,1,,A,13SeLS7P1j15l@FHcA<PM?vN05`P,0*26'),
])
def test_format_nmea(source, message, addr, timestamp, port, expected):
    messages = [(message, addr, timestamp, port)]
    formatted = list(format_nmea(messages, source))
    expected = [expected]
    assert formatted == expected


@pytest.mark.parametrize("source,message,addr,timestamp,port,expected", [
    ('source', '', '127.0.0.1', 123, 0, []),
    ('source', ' ', '127.0.0.1', 123, 0, []),
    ('source', 'message1\n', '127.0.0.1', 123, 0, ['\\t:source,s:127.0.0.1,c:123*58\\message1']),
    ('source', 'message1\nmessage2', '127.0.0.1', 123, 0,
     ['\\t:source,s:127.0.0.1,c:123*58\\message1', '\\t:source,s:127.0.0.1,c:123*58\\message2']
     ),
])
def test_multiline(source, message, addr, timestamp, port,  expected):
    messages = [(message, addr, timestamp, port)]
    formatted = list(format_nmea(messages, source))
    assert formatted == expected
