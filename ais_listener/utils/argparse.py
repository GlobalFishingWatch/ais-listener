"""
Utilities for use with argparse
"""

from datetime import datetime
import argparse
import logging
import os
import sys
from enum import Enum
from enum import unique


@unique
class ExitCode(Enum):
    SUCCESS = 0
    FAIL = 1


def valid_date(s):
    """
    Use with argparse to validate a date parameter

    Example Usage:
    parser.add_argument('--start_date', type=valid_date,
                    help='Start date for the pipeline. '
                         'Format: YYYY-MM-DD (default: %(default)s)',
                    default='2019-01-01')
    """

    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


def pretty_print_args(args):
    arg_str = '\n'.join(f'  {k}={v}' for k, v in vars(args).items())
    return f'Executing with parameters:\n{arg_str}'


def setup_logging(verbosity):
    base_loglevel = getattr(logging,
                            (os.getenv('LOGLEVEL', 'WARNING')).upper())
    verbosity = min(verbosity, 2)
    loglevel = base_loglevel - (verbosity * 10)


    # create logger
    log = logging.getLogger('main')
    log.propagate = False
    log.setLevel(loglevel)

    # create console handler and set level
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(loglevel)

    # create formatter
    formatter = logging.Formatter('%(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    log.addHandler(ch)

    return log
