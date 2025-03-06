import pytest

from socket_listener.utils import yaml_load


@pytest.mark.parametrize("filename,host,port", [
    ('config/TCP-client-kystverket.yaml', "153.44.253.27", 5631),
])
def test_yaml_load(filename, host, port):
    config = yaml_load(filename)
    assert config['host'] == host
    assert config['port'] == port
