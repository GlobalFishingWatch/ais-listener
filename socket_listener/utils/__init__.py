"""Utilities package."""
import yaml
from pathlib import Path
from cloudpathlib import CloudPath


from .logger import setup_logger


def pretty_print_args(args: dict) -> str:
    """Returns a dictionary as string, pretty printed."""
    arg_str = "\n".join(f"  {k}={v}" for k, v in args.items())

    return f"Executing with parameters:\n{arg_str}"


def yaml_load(filename: str) -> dict:
    """Loads yaml file from filesystem or google cloud storage."""
    path = CloudPath(filename) if filename.startswith('gs://') else Path(filename)
    with path.open('r') as f:
        return yaml.safe_load(f)


__all__ = [  # functions importable directly from package.
    setup_logger
]
