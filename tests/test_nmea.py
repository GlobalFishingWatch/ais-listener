import pytest
import time
from util.nmea import format_nmea

source_port_map = {
    0: 'ais-listener',
    1: 'source1'
}


@pytest.mark.parametrize("message,addr,timestamp,port,expected", [
    ('message', '127.0.0.1', 123, 0,
        '\\t:ais-listener,c:123*43\\message'),
    ('message', '127.0.0.1', 123, 1,
        '\\t:source1,c:123*27\\message'),
    ('message', '127.0.0.1', 123, 2,
        '\\t:ais-listener-2,c:123*5C\\message'),
    ('message\n', '127.0.0.1', 123, 0,
        '\\t:ais-listener,c:123*43\\message'),
    ('!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F', '127.0.0.1', 123, 0,
        '\\t:ais-listener,c:123*43\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F'),
    ('\\t:other\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F', '127.0.0.1', 123, 1,
        '\\t:source1,c:123*27\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F'),
    ('\\t:other,s:station\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F', '127.0.0.1', 123, 1,
        '\\t:source1,s:station,c:123*38\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F'),
    ('\\t:other,c:999,s:station\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F', '127.0.0.1', 123, 1,
        '\\t:source1,c:999,s:station*31\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F'),
    ('\\c:bad_value\\message', '127.0.0.1', 123, 0,
        '\\c:bad_value\\message'),
    ('\\s:rMT5858,*0E\\!AIVDM,1,1,,A,13SeLS7P1j15l@FHcA<PM?vN05`P,0*26', '127.0.0.1', 123, 1,
     '\\s:rMT5858,t:source1,c:123*29\\!AIVDM,1,1,,A,13SeLS7P1j15l@FHcA<PM?vN05`P,0*26'),
])
def test_format_nmea(message, addr, timestamp, port, expected):
    messages = [(message, addr, timestamp, port)]
    formatted = list(format_nmea(messages, source_port_map))
    expected = [expected]
    assert formatted == expected

@pytest.mark.parametrize("message,addr,timestamp,port,expected", [
    ('', '127.0.0.1', 123, 0,
     []),
    ('message1\n', '127.0.0.1', 123, 0,
     ['\\t:ais-listener,c:123*43\\message1']
     ),
    ('message1\nmessage2', '127.0.0.1', 123, 0,
     ['\\t:ais-listener,c:123*43\\message1', '\\t:ais-listener,c:123*43\\message2']
    ),
])
def test_multiline(message, addr, timestamp, port,  expected):
    messages = [(message, addr, timestamp, port)]
    formatted = list(format_nmea(messages, source_port_map))
    assert formatted == expected
