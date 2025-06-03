"""Command-line interface for socket-listener service."""
import sys
import logging
import argparse
from pathlib import Path
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
HELP_LOG_FILE = "If True, logs will be written to a file."
HELP_WORKDIR = "Directory to use for saving outputs, logs, and other artifacts."

HELP_RECEIVER = "Receives data continuosly from network sockets."
HELP_CONFIG_FILE = f"Path to config file. If passed, rest of CLI args are ignored {HELP_DEFAULT}."
HELP_MAX_PACKET_SIZE = f"The maximum amount of data to be received at once {HELP_DEFAULT}."
HELP_DELIMITER = f"Delimiter to use when splitting incoming packets into messages {HELP_DEFAULT}."
HELP_IP_CLIENT_MAPPING_FILE = f"Path to (IP -> client_name) mappings {HELP_DEFAULT}."
HELP_MONITOR_DELAY = f"Number of seconds between each log entry of ThreadMonitor {HELP_DEFAULT}."

HELP_PUBSUB = "Enable publication to Google PubSub service."
HELP_PUB_PROJ = f"GCP project id {HELP_DEFAULT}."
HELP_PUB_TOPIC = f"Google Pub/Sub topic id {HELP_DEFAULT}."

HELP_TRANSMITTER = "Sends lines from a file through network sockets [useful for testing]."
HELP_PATH = f"Path to the file or folder containing the data to send {HELP_DEFAULT}."
HELP_DELAY = f"Delay in seconds between sent messages {HELP_DEFAULT}."
HELP_CHUNK_SIZE = f"Amount of messages to be sent in a single packet {HELP_DEFAULT}."
HELP_FIRST_N = f"Only send the first n messages of the file and then stop. {HELP_DEFAULT}."

DEFAULT_PROTOCOL = "UDP"
DEFAULT_PATH = "sample/nmea.txt"
DEFAULT_PUB_PROJ = "world-fishing-827"
DEFAULT_PUB_TOPIC = "nmea-stream-dev"
DEFAULT_DELIMITER = "\n"

TEMPLATE_LOG_FILENAME = "socket-listener-{operation}.log"
DEFAULT_WORKDIR = "workdir"


def formatter():
    """Returns a formatter for argparse help."""

    def formatter(prog):
        return argparse.RawTextHelpFormatter(prog, max_help_position=50)

    return formatter


def defaults():
    return {
        "protocol": DEFAULT_PROTOCOL,
        "host": "0.0.0.0",
        "port": 10110,
        "daemon_thread": False,
        "max_packet_size": 4096,
        "delimiter": DEFAULT_DELIMITER,
        "ip_client_mapping_file": None,
        "pubsub": False,
        "pubsub_topic": DEFAULT_PUB_TOPIC,
        "pubsub_project": DEFAULT_PUB_PROJ
    }


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
    add("-c", "--config-file", type=str, metavar=" ", help=HELP_CONFIG_FILE)
    add("-w", "--workdir", type=str, default=DEFAULT_WORKDIR, metavar=" ", help=HELP_WORKDIR)
    add("-v", "--verbose", action="store_true", help=HELP_VERBOSE)
    add("-l", "--log-to-file", action="store_true", help=HELP_LOG_FILE),
    add("--no-rich-logging", action="store_true", help=HELP_NO_RICH_LOGGING)
    add("--protocol", type=str, metavar=" ", help=HELP_PROTOCOL)
    add("--host", type=str, metavar=" ", help=HELP_HOST)
    add("--port", type=int, metavar=" ", help=HELP_PORT)
    add("--daemon-thread", action="store_true", default=None, help=HELP_DAEMON_THREAD)

    # Subparsers
    subparsers = parser.add_subparsers(dest="operation", required=True)

    p = subparsers.add_parser(
        "receiver", formatter_class=formatter(), parents=[common], help=HELP_RECEIVER)

    p.set_defaults(func=receivers.run)
    add = p.add_argument
    add("--max-packet-size", type=int, metavar=" ", help=HELP_MAX_PACKET_SIZE)
    add("--delimiter", type=str, metavar=" ", help=HELP_DELIMITER)
    add("--ip-client-mapping-file", type=str, metavar=" ", help=HELP_IP_CLIENT_MAPPING_FILE)
    add("--thread-monitor-delay", type=float, metavar=" ", help=HELP_MONITOR_DELAY)

    add = p.add_argument_group("Google Pub/Sub sink").add_argument
    add("--pubsub", action="store_true", default=None, help=HELP_PUBSUB)
    add("--pubsub-project", type=str, metavar=" ", help=HELP_PUB_PROJ)
    add("--pubsub-topic", type=str, metavar=" ", help=HELP_PUB_TOPIC)

    p = subparsers.add_parser(
        "transmitter", formatter_class=formatter(), parents=[common], help=HELP_TRANSMITTER)

    p.set_defaults(func=transmitters.run)
    add = p.add_argument
    add("--chunk-size", type=int, default=50, metavar=" ", help=HELP_CHUNK_SIZE)
    add("-n", "--first-n", type=int, default=None, metavar=" ", help=HELP_FIRST_N)
    add("-d", "--delay", type=float, default=1, metavar=" ", help=HELP_DELAY)
    add("-p", "--path", type=str, default=DEFAULT_PATH, metavar=" ", help=HELP_PATH)

    return parser


def cli(args):
    parser = define_parser()
    ns = parser.parse_args(args=args or ["--help"])

    verbose = ns.verbose
    no_rich_logging = ns.no_rich_logging
    func = ns.func
    config_file = ns.config_file
    log_to_file = ns.log_to_file
    workdir = ns.workdir

    log_file = None
    if log_to_file:
        log_file = Path(workdir) / TEMPLATE_LOG_FILENAME.format(operation=ns.operation)

    setup_logger(
        verbose=verbose,
        rich=not no_rich_logging,
        force=True,
        warning_level=[
            "google.cloud.pubsub_v1.publisher",
            "urllib3.connectionpool",
            "google.auth.transport.requests",
        ],
        log_file=log_file,
    )

    # Delete CLI configuration from parsed namespace.
    del ns.verbose
    del ns.no_rich_logging
    del ns.func
    del ns.config_file
    del ns.log_to_file
    del ns.operation
    del ns.workdir

    config = {}
    if config_file is not None:
        logger.info(f"Loading config file from {config_file}.")
        config = yaml_load(config_file)

    cli_args = vars(ns)

    defaults_args = {k: v for k, v in defaults().items() if k in cli_args}
    cli_args = {k: v for k, v in cli_args.items() if v is not None}

    # cli_args takes precedence over config file and config file over defaults.
    config = ChainMap(cli_args, config, defaults_args)

    logger.info(f"Starting {NAME_TPL.format(version=__version__)}")
    logger.info(pretty_print_args(config))
    if log_file:
        logger.info(f"File logging enabled. Logs will be saved to: {log_file}")

    return func(**config)


def main():
    cli(sys.argv[1:])


if __name__ == "__main__":
    main()
