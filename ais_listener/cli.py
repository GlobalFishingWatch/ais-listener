"""Module with command-line interface for ais-listener serivce."""
import os
import sys
import math
import logging
import argparse

from ais_listener.utils import setup_logger, pretty_print_args
from ais_listener.version import __version__
from ais_listener import transmitters
from ais_listener import receivers


logger = logging.getLogger(__name__)


NAME_TPL = "AIS Listener (v{version})."
DESCRIPTION = (
    "A TCP/UDP server that receives NMEA-encoded AIS messages "
    "and publish them to configured outputs."
)


HELP_DEFAULT = "(default: %(default)s)"
HELP_NO_RICH_LOGGING = "Disable rich logging (useful prof production environments)."
HELP_VERBOSE = "Set logger level to DEBUG."
HELP_PROJECT = f"GCP project id {HELP_DEFAULT}."

HELP_RECEIVER = "Command to receive data from a TCP or UDP sockets."
HELP_CONFIG_FILE = f"Path to configuration file sources to listen {HELP_DEFAULT}."
HELP_REC_PORT = f"UDP/TCP port {HELP_DEFAULT}."
HELP_MAX_PACKET_SIZE = f"Máximum size in bytes for the internal buffer {HELP_DEFAULT}."
HELP_MAX_RETRIES = f"Max. retries if a connection fails {HELP_DEFAULT}."
HELP_RETRY_DELAY = f"Initial retry delay when a connection fails {HELP_DEFAULT}."


HELP_TRANSMITTER = "Command to send lines from a file through TCP or UDP sockets."
HELP_PROTOCOL = f"UDP or TCP {HELP_DEFAULT}."
HELP_HOST = f"For UDP, the IP address of receiver to send to {HELP_DEFAULT}.",
HELP_PORT = f"UDP/TCP port {HELP_DEFAULT}."

HELP_DEFAULT = f"UDP/TCP port {HELP_DEFAULT}."
HELP_FILEPATH = f"Path to the file containing the data to send {HELP_DEFAULT}."
HELP_DELAY = f"Delay in seconds between sent messages {HELP_DEFAULT}."

DEFAULT_CONFIG_FILE = "sample/sources.yaml"
DEFAULT_FILEPATH = "sample/nmea.txt"
DEFAULT_PROJECT = "world-fishing-827"
DEFAULT_PROTOCOL = "UDP"


def formatter():
    """Returns a formatter for argparse help."""

    def formatter(prog):
        return argparse.RawTextHelpFormatter(prog, max_help_position=50)

    return formatter


def define_parser():
    # Main parser
    parser = argparse.ArgumentParser(
        prog=NAME_TPL.format(version=__version__),
        description=DESCRIPTION,
        # epilog=EPILOG,
        formatter_class=formatter(),
    )
    add = parser.add_argument

    # Common arguments
    add("-v", "--verbose", action="store_true", help=HELP_VERBOSE)
    add("--no-rich-logging", action="store_true", help=HELP_NO_RICH_LOGGING)
    add("--project", type=str, default=DEFAULT_PROJECT, metavar=" ", help=HELP_PROJECT)
    add("--protocol", type=str, default=DEFAULT_PROTOCOL, metavar=" ", help=HELP_PROTOCOL)

    # Subparsers
    subparsers = parser.add_subparsers(required=True)

    p = subparsers.add_parser("receiver", formatter_class=formatter(), help=HELP_RECEIVER)
    p.set_defaults(func=receivers.run)
    add = p.add_argument

    add("--config-file", type=str, default=DEFAULT_CONFIG_FILE, metavar=" ", help=HELP_CONFIG_FILE)
    add("--host", type=str, default="localhost", metavar=" ", help=HELP_HOST)
    add("--port", type=int, default=10110, metavar=" ", help=HELP_REC_PORT)
    add("--max-packet-size", type=int, default=4096, metavar=" ", help=HELP_MAX_PACKET_SIZE)
    add("--max-retries", type=int, default=math.inf, metavar=" ", help=HELP_MAX_RETRIES)
    add("--init-retry-delay", type=float, default=1, metavar=" ", help=HELP_RETRY_DELAY)

    p = subparsers.add_parser("transmitter", help="Send lines from a file.")
    p.set_defaults(func=transmitters.run)
    add = p.add_argument

    add("--host", type=str, default="localhost", metavar=" ", help=HELP_HOST)
    add("--port", type=int, default=10110, metavar=" ", help=HELP_PORT)
    add("--delay", type=float, default=1, metavar=" ", help=HELP_DELAY)
    add("--filepath", type=str, default=DEFAULT_FILEPATH, metavar=" ", help=HELP_FILEPATH)

    return parser


def cli(args):
    parser = define_parser()
    ns = parser.parse_args(args=args or ["--help"])

    # For some reason, google client is not inferring project from environment.
    os.environ["GOOGLE_CLOUD_PROJECT"] = ns.project

    verbose = ns.verbose
    no_rich_logging = ns.no_rich_logging
    func = ns.func

    # Delete CLI configuration from parsed namespace.
    del ns.verbose
    del ns.no_rich_logging
    del ns.func
    del ns.project

    logger_level = logging.INFO
    if verbose:
        logger_level = logging.DEBUG

    setup_logger(level=logger_level, rich=not no_rich_logging, force=True)

    logger.info(f"Starting {NAME_TPL.format(version=__version__)}")
    args = vars(ns)
    logger.info(pretty_print_args(args))

    func(**args)


def main():
    cli(sys.argv[1:])


if __name__ == "__main__":
    main()
