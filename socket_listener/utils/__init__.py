"""Utilities package."""
import yaml
import itertools
from pathlib import Path
from typing import Iterable, Generator

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


def get_subclasses_map(cls):
    """Returns a map of .name -> subclass of parent class cls."""
    subclasses = {}
    for subclass in cls.__subclasses__():
        subclasses[subclass.name] = subclass

    return subclasses


def chunked_it(iterable: Iterable, n: int) -> Generator:
    """Splits an iterable into iterator chunks of length n. The last chunk may be shorter."""
    if n < 1:
        raise ValueError('n must be at least one')

    it = iter(iterable)
    for x in it:
        yield itertools.chain((x,), itertools.islice(it, n - 1))


__all__ = [  # functions importable directly from package.
    setup_logger
]
