import yaml
from collections import defaultdict
from pathlib import Path
from cloudpathlib import CloudPath

def load_source_port_map(filename):
    path = CloudPath(filename) if filename.startswith('gs://') else Path(filename)
    with path.open('r') as f:
        return yaml.safe_load(f)['sources']
