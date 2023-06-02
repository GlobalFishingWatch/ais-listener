import pytest
import time
from util.nmea import format_nmea

source_ip_map = {
    '127.0.0.1': 'localhost'
}


@pytest.mark.parametrize("message,source,timestamp,expected", [
    ('message', 'source', 123,
        '\\t:source,c:123*16\\message'),
    ('message', '127.0.0.1', 123,
        '\\t:localhost,c:123*66\\message'),
    ('!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F', 'source', 123,
        '\\t:source,c:123*16\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F'),
    ('\\t:other\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F', 'source', 123,
        '\\t:source,c:123*16\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F'),
    ('\\t:other,s:station\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F', 'source', 123,
        '\\t:source,s:station,c:123*09\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F'),
    ('\\t:other,c:999,s:station\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F', 'source', 123,
        '\\t:source,c:999,s:station*00\\!AIVDM,1,1,,A,13prmQ?P001EOA4OC3h@u?vl20SR,0*7F'),
    ('\\c:bad_value\\message', '127.0.0.1', 123,
        '\\c:bad_value\\message'),
    ('\\s:rMT5858,*0E\\!AIVDM,1,1,,A,13SeLS7P1j15l@FHcA<PM?vN05`P,0*26', '127.0.0.1', 123,
     '\\s:rMT5858,t:localhost,c:123*68\\!AIVDM,1,1,,A,13SeLS7P1j15l@FHcA<PM?vN05`P,0*26'),
])
def test_format_nmea(message, source, timestamp, expected):
    messages = [(message, source, timestamp)]
    formatted = list(format_nmea(messages, source_ip_map))
    expected = [expected]
    assert formatted == expected
