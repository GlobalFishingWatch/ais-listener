import pytest
from socket_listener.utils import yaml_load, chunked_it


@pytest.mark.parametrize("filename,port", [
    ('config/UDP-ais.yaml', 10110),
])
def test_yaml_load(filename, port):
    config = yaml_load(filename)
    assert config['port'] == port


@pytest.mark.parametrize("lst, n, expected", [
    (
        [1, 2, 3, 4, 5],
        3,
        [[1, 2, 3], [4, 5]]),
])
def test_chunk_it(lst, n, expected):
    assert [list(x) for x in chunked_it(lst, n)] == expected
