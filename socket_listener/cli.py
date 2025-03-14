"""Command-line interface for socket-listener service."""
import sys
import logging
import argparse
from collections import ChainMap

from socket_listener import receivers
from socket_listener import transmitters
from socket_listener.version import __version__
from socket_listener.utils import setup_logger, pretty_print_args, yaml_load

logger = logging.getLogger(__name__)


NAME_TPL = "Socket Listener (v{version})."
DESCRIPTION = (
    "A service that receives messages through network sockets "
    "and publish them to desired destinations."
)
EPILOG = (
    "Example: \n"
    "    socket-listener receiver --protocol UDP --port 10112 --max-packet-size 2048"
)

HELP_DEFAULT = "(default: %(default)s)"
HELP_NO_RICH_LOGGING = "Disable rich logging [useful for production environments]."
HELP_VERBOSE = "Set logger level to DEBUG."
HELP_PROTOCOL = f"Network protocol to use {HELP_DEFAULT}."
HELP_PORT = f"Port to use {HELP_DEFAULT}."
HELP_HOST = f"IP to use {HELP_DEFAULT}."
HELP_DAEMON_THREAD = "Run main process in a daemonic thread [Useful for testing]."

HELP_RECEIVER = "Receives data continuosly from network sockets."
HELP_CONFIG_FILE = f"Path to config file. If passed, rest of CLI args are ignored {HELP_DEFAULT}."
HELP_MAX_PACKET_SIZE = f"The maximum amount of data to be received at once {HELP_DEFAULT}."
HELP_DELIMITER = f"Delimiter to use when splitting incoming packets into messages {HELP_DEFAULT}."
HELP_IP_CLIENT_MAPPING_FILE = f"Path to (IP -> client_name) mappings {HELP_DEFAULT}."

HELP_PUBSUB = "Enable publication to Google PubSub service."
HELP_PUB_PROJ = f"GCP project id {HELP_DEFAULT}."
HELP_PUB_TOPIC = f"Google Pub/Sub topic id {HELP_DEFAULT}."

HELP_TRANSMITTER = "Sends lines from a file through network sockets [useful for testing]."
HELP_FILEPATH = f"Path to the file containing the data to send {HELP_DEFAULT}."
HELP_DELAY = f"Delay in seconds between sent messages {HELP_DEFAULT}."
HELP_CHUNK_SIZE = f"Amount of messages to be sent in a single packet {HELP_DEFAULT}."
HELP_FIRST_N = f"Only send the first n messages of the file and then stop. {HELP_DEFAULT}."

DEFAULT_PROTOCOL = "UDP"
DEFAULT_FILEPATH = "sample/nmea.txt"
DEFAULT_PUB_PROJ = "world-fishing-827"
DEFAULT_PUB_TOPIC = "NMEA"
DEFAULT_DELIMITER = "\n"


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
        epilog=EPILOG,
        formatter_class=formatter(),
    )

    common = argparse.ArgumentParser(add_help=False)

    add = common.add_argument
    # Common arguments
    add("-v", "--verbose", action="store_true", help=HELP_VERBOSE)
    add("-c", "--config-file", type=str, metavar=" ", help=HELP_CONFIG_FILE)
    add("--no-rich-logging", action="store_true", help=HELP_NO_RICH_LOGGING)
    add("--protocol", type=str, default=DEFAULT_PROTOCOL, metavar=" ", help=HELP_PROTOCOL)
    add("--host", type=str, default="0.0.0.0", metavar=" ", help=HELP_HOST)
    add("--port", type=int, default=10110, metavar=" ", help=HELP_PORT)
    add("--daemon-thread", action="store_true", help=HELP_DAEMON_THREAD)

    # Subparsers
    subparsers = parser.add_subparsers(required=True)

    p = subparsers.add_parser(
        "receiver", formatter_class=formatter(), parents=[common], help=HELP_RECEIVER)

    p.set_defaults(func=receivers.run)
    add = p.add_argument
    add("--max-packet-size", type=int, default=4096, metavar=" ", help=HELP_MAX_PACKET_SIZE)
    add("--delimiter", type=str, default=DEFAULT_DELIMITER, metavar=" ", help=HELP_DELIMITER)
    add("--ip-client-mapping-file", type=str, metavar=" ", help=HELP_IP_CLIENT_MAPPING_FILE)

    add = p.add_argument_group("Google Pub/Sub sink").add_argument
    add("--pubsub", action="store_true", help=HELP_PUBSUB)
    add("--pubsub-project", type=str, default=DEFAULT_PUB_PROJ, metavar=" ", help=HELP_PUB_PROJ)
    add("--pubsub-topic", type=str, default=DEFAULT_PUB_TOPIC, metavar=" ", help=HELP_PUB_TOPIC)

    p = subparsers.add_parser(
        "transmitter", formatter_class=formatter(), parents=[common], help=HELP_TRANSMITTER)

    p.set_defaults(func=transmitters.run)
    add = p.add_argument
    add("--chunk-size", type=int, default=50, metavar=" ", help=HELP_CHUNK_SIZE)
    add("-n", "--first-n", type=int, default=None, metavar=" ", help=HELP_FIRST_N)
    add("-d", "--delay", type=float, default=1, metavar=" ", help=HELP_DELAY)
    add("-f", "--filepath", type=str, default=DEFAULT_FILEPATH, metavar=" ", help=HELP_FILEPATH)

    return parser


def cli(args):
    parser = define_parser()
    ns = parser.parse_args(args=args or ["--help"])

    verbose = ns.verbose
    no_rich_logging = ns.no_rich_logging
    func = ns.func
    config_file = ns.config_file

    # Delete CLI configuration from parsed namespace.
    del ns.verbose
    del ns.no_rich_logging
    del ns.func
    del ns.config_file

    config = {}
    if config_file is not None:
        logger.info("Loading config file.")
        config = yaml_load(config_file)

    cli_args = vars(ns)

    # cli_args takes precedence over config file.
    config = ChainMap(cli_args, config)

    setup_logger(verbose=verbose, rich=not no_rich_logging, force=True)

    logger.info(f"Starting {NAME_TPL.format(version=__version__)}")
    logger.info(pretty_print_args(config))

    return func(**config)


def main():
    cli(sys.argv[1:])


if __name__ == "__main__":
    main()
