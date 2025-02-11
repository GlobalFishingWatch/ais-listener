"""Module with command-line interface for ais-listener serivce."""
import os
import logging
import argparse
import rich_argparse

from ais_listener.pipeline import Pipeline
from ais_listener.utils import setup_logger, pretty_print_args
from ais_listener.version import __version__

logger = logging.getLogger(__name__)


NAME_TPL = "AIS Listener (v{version})."
DESCRIPTION = (
    "A TCP/UDP server that receives NMEA-encoded AIS messages "
    "and publish them to configured outputs."
)


HELP_DEFAULT = "(default: %(default)s)"
HELP_NO_RICH_LOGGING = "Disable rich logging (useful prof production environments)."
HELP_VERBOSE = "Set logger level to DEBUG."


def formatter(rich: bool = False):
    """Returns a formatter for argparse help."""

    def formatter(prog):
        if rich:
            return rich_argparse.RawTextRichHelpFormatter(prog, max_help_position=50)
        else:
            return argparse.RawTextHelpFormatter(prog, max_help_position=50)

    return formatter


def define_parser():
    parser = argparse.ArgumentParser(
        prog=NAME_TPL.format(version=__version__),
        description=DESCRIPTION,
        # epilog=EPILOG,
        formatter_class=formatter(),
    )

    subparsers = parser.add_subparsers(dest="operation", required=True)
    # Common arguments

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help=HELP_VERBOSE
    )

    parser.add_argument(
        "--no-rich-logging",
        action="store_true",
        default=False,
        help=HELP_NO_RICH_LOGGING
    )

    parser.add_argument(
        "--project",
        type=str,
        default="world-fishing-827",
        metavar=" ",
        help=f"GCP project id {HELP_DEFAULT}.",
    )

    # operations
    receiver_args = subparsers.add_parser(
        "receiver",
        formatter_class=formatter(),
        help="Receive nmea lines from a TCP ot UDP transmitter."
    )

    receiver_args.add_argument(
        "--buffer-size",
        type=int,
        default=4096,
        metavar=" ",
        help=f"Size in bytes for the internal buffer {HELP_DEFAULT}.",
    )

    receiver_args.add_argument(
        "--config_file",
        type=str,
        default="sample/sources.yaml",
        metavar=" ",
        help=f"File to read to get mapping of listening ports to source names {HELP_DEFAULT}.",
    )

    transmitter_args = subparsers.add_parser(
        "transmitter",
        help="Send lines from a file."
    )

    transmitter_args.add_argument(
        "--protocol",
        type=str,
        default="UDP",
        metavar=" ",
        help=f"UDP or TCP {HELP_DEFAULT}.",
    )

    transmitter_args.add_argument(
        "--receiver-ip",
        type=str,
        default="localhost",
        metavar=" ",
        help=f"For UDP, the IP address of receiver to send to {HELP_DEFAULT}.",
    )

    transmitter_args.add_argument(
        "--port",
        type=int,
        default=10110,
        metavar=" ",
        help=f"UDP/TCP port {HELP_DEFAULT}.",
    )

    transmitter_args.add_argument(
        "--filename",
        type=str,
        default="sample/nmea.txt",
        metavar=" ",
        help=f"Name of file to read from {HELP_DEFAULT}.",
    )

    transmitter_args.add_argument(
        "--delay",
        type=float,
        default=1,
        metavar=" ",
        help=f"Delay in seconds between messages {HELP_DEFAULT}.",
    )

    return parser


def main():
    parser = define_parser()
    ns = parser.parse_args()

    # For some reason, google client is not inferring project from environment.
    os.environ["GOOGLE_CLOUD_PROJECT"] = ns.project

    verbose = ns.verbose
    no_rich_logging = ns.no_rich_logging

    # Delete CLI configuration from parsed namespace.
    del ns.verbose
    del ns.no_rich_logging

    logger_level = logging.INFO
    if verbose:
        logger_level = logging.DEBUG

    setup_logger(level=logger_level, rich=not no_rich_logging, force=True)

    logger.info(f"Starting {NAME_TPL.format(version=__version__)}")
    logger.info(pretty_print_args(vars(ns)))

    _ = Pipeline(ns).run()


if __name__ == "__main__":
    main()
