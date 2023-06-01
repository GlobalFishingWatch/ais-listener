import yaml
from collections import defaultdict
from pathlib import Path
from cloudpathlib import CloudPath

def load_source_ip_map(filename, default_source=None):
    path = CloudPath(filename) if filename.startswith('gs://') else Path(filename)
    with path.open('r') as f:
        sources = yaml.safe_load(f)['sources']
        if default_source is not None:
            d = defaultdict(lambda:default_source)
            d.update(sources)
        else:
            d = sources
        return d