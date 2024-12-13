"""Utilities for use with argparse."""

import argparse
from datetime import date

ERROR_INVALID_DATE_FORMAT = "Invalid date format."


def valid_date(date_str: str):
    """Validation function to use as argparse argument type.

    Example Usage:
        parser.add_argument(
            '--start_date',
            type=valid_date,
            help='Start date for the pipeline. Format: YYYY-MM-DD (default: %(default)s)',
            default='2019-01-01'
        )
    """

    try:
        return date.fromisoformat(date_str)
    except Exception as e:
        raise argparse.ArgumentTypeError(f"{ERROR_INVALID_DATE_FORMAT} \n {e}")


def pretty_print_args(args: dict):
    arg_str = "\n".join(f"  {k}={v}" for k, v in args.items())

    return f"Executing with parameters:\n{arg_str}"
