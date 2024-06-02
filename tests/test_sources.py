import pytest
from util.sources import load_config_file


@pytest.mark.parametrize("filename,port,source", [
    ('sample/sources.yaml', 10110, 'ais-listener'),
    # ('gs://scratch-paul-ttl100/ais-listener/sources.yaml', '127.0.0.1', 'localhost'),
])
def test_load_config(filename, port, source):
    config = load_config_file(filename)
    sources = {item['source']: item for item in config['sources']}
    assert sources[source]['port'] == port
