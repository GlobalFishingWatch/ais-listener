"""Utilities package."""
from .logger import setup_logger


def pretty_print_args(args: dict):
    arg_str = "\n".join(f"  {k}={v}" for k, v in args.items())

    return f"Executing with parameters:\n{arg_str}"


__all__ = [  # functions importable directly from package.
    setup_logger, pretty_print_args
]
