import pytest
from util.sources import load_source_port_map


@pytest.mark.parametrize("filename,port,expected", [
    ('sample/sources.yaml', 10110, 'ais-listener'),
    # ('gs://scratch-paul-ttl100/ais-listener/sources.yaml', '127.0.0.1', 'localhost'),
])
def test_load_source_port_map(filename, port, expected):
    source_port_map = load_source_port_map(filename)
    assert source_port_map[port] == expected
