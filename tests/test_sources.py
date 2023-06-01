import pytest
from util.sources import load_source_ip_map



@pytest.mark.parametrize("filename,source_ip,expected", [
    ('sample/sources.yaml', '127.0.0.1', 'localhost'),
    # ('gs://scratch-paul-ttl100/ais-listener/sources.yaml', '127.0.0.1', 'localhost'),
])
def test_load_source_ip_map(filename, source_ip, expected):
    source_ip_map = load_source_ip_map(filename)
    assert source_ip_map[source_ip] == expected

def test_load_source_ip_map_with_default():
    default_source = 'notfound'
    source_ip_map = load_source_ip_map('sample/sources.yaml', default_source=default_source)
    assert source_ip_map['127.0.0.1'] == 'localhost'
    assert source_ip_map['0.0.0.0'] == default_source

def test_load_source_ip_map_without_default():
    source_ip_map = load_source_ip_map('sample/sources.yaml', default_source=None)
    with pytest.raises(KeyError):
        assert source_ip_map['0.0.0.0'] == ''
