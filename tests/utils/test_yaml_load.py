import pytest

from socket_listener.utils import yaml_load


@pytest.mark.parametrize("filename,port", [
    ('config/UDP-ais.yaml', 10110),
])
def test_yaml_load(filename, port):
    config = yaml_load(filename)
    assert config['port'] == port
