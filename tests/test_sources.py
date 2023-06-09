import pytest
from util.sources import load_source_port_map



@pytest.mark.parametrize("filename,port,expected", [
    ('sample/sources.yaml', 10110, 'ais-listener'),
    # ('gs://scratch-paul-ttl100/ais-listener/sources.yaml', '127.0.0.1', 'localhost'),
])
def test_load_source_ip_map(filename, port, expected):
    source_port_map = load_source_port_map(filename)
    assert source_port_map[port] == expected

def test_load_source_ip_map_with_default():
    default_source = 'notfound'
    source_port_map = load_source_port_map('sample/sources.yaml', default_source=default_source)
    assert source_port_map[10110] == 'ais-listener'
    assert source_port_map[9999] == default_source

def test_load_source_ip_map_without_default():
    source_port_map = load_source_port_map('sample/sources.yaml', default_source=None)
    with pytest.raises(KeyError):
        assert source_port_map[9999] == ''
