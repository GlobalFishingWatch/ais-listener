"""Command-line interface for socket-listener service."""
import sys
import logging
import argparse

from gfw.common.logging import LoggerConfig
from gfw.common.cli import CLI, Option, ParametrizedCommand

from socket_listener import receivers
from socket_listener import transmitters
from socket_listener.version import __version__


logger = logging.getLogger(__name__)


NAME_TPL = "Socket Listener (v{version})."
DESCRIPTION = (
    "A service that receives messages through network sockets "
    "and publish them to desired destinations."
)

HELP_NO_RICH_LOGGING = "Disable rich logging [useful for production environments]."
HELP_VERBOSE = "Set logger level to DEBUG."
HELP_PROTOCOL = "Network protocol to use."
HELP_PORT = "Port to use."
HELP_HOST = "IP to use."
HELP_DAEMON_THREAD = "Run main process in a daemonic thread [Useful for testing]."
HELP_LOG_FILE = "If True, logs will be written to a file."
HELP_WORKDIR = "Directory to use for saving outputs, logs, and other artifacts."

HELP_RECEIVER = "Receives data continuosly from network sockets."
HELP_CONFIG_FILE = "Path to config file. If passed, rest of CLI args are ignored."
HELP_MAX_PACKET_SIZE = "The maximum amount of data to be received at once."
HELP_DELIMITER = "Delimiter to use when splitting incoming packets into messages."
HELP_IP_CLIENT_MAPPING_FILE = "Path to (IP -> client_name) mappings."
HELP_MONITOR_DELAY = "Number of seconds between each log entry of ThreadMonitor."

HELP_PUBSUB = "Enable publication to Google PubSub service."
HELP_PUB_PROJ = "GCP project id."
HELP_PUB_TOPIC = "Google Pub/Sub topic id."
HELP_FORMAT = "Data format to use for Google Pub/Sub messages."

HELP_TRANSMITTER = "Sends lines from a file through network sockets [useful for testing]."
HELP_PATH = "Path to the file or folder containing the data to send."
HELP_DELAY = "Delay in seconds between sent messages."
HELP_CHUNK_SIZE = "Amount of messages to be sent in a single packet."
HELP_SPLITTER = "Function to use for splitting the input files into chunks."
HELP_FIRST_N = "Only send the first n messages of the file and then stop.."

DEFAULT_PROTOCOL = "UDP"
DEFAULT_PATH = "sample/nmea.txt"
DEFAULT_PUB_PROJ = "world-fishing-827"
DEFAULT_PUB_TOPIC = "nmea-stream-dev"
DEFAULT_FORMAT = "raw"
DEFAULT_DELIMITER = "\n"

DEFAULT_WORKDIR = "workdir"


def formatter():
    """Returns a formatter for argparse help."""

    def formatter(prog):
        return argparse.RawTextHelpFormatter(prog, max_help_position=50)

    return formatter


def cli(args):
    receiver_cmd = ParametrizedCommand(
        name="receiver",
        description=HELP_RECEIVER,
        options=[
            Option("--max-packet-size", type=int, default=4096, help=HELP_MAX_PACKET_SIZE),
            Option("--delimiter", type=str, default=DEFAULT_DELIMITER, help=HELP_DELIMITER),
            Option("--ip-client-mapping-file", type=str, help=HELP_IP_CLIENT_MAPPING_FILE),
            Option("--thread-monitor-delay", type=float, help=HELP_MONITOR_DELAY),
            Option("--pubsub", type=bool, default=False, help=HELP_PUBSUB),
            Option("--pubsub-project", type=str, default=DEFAULT_PUB_PROJ,  help=HELP_PUB_PROJ),
            Option("--pubsub-topic", type=str, default=DEFAULT_PUB_TOPIC, help=HELP_PUB_TOPIC),
            Option("--pubsub-data-format", type=str, default=DEFAULT_FORMAT, help=HELP_FORMAT)
        ],
        run=lambda config: receivers.run(**vars(config)),
    )

    transmitter_cmd = ParametrizedCommand(
        name="transmitter",
        description=HELP_TRANSMITTER,
        options=[
            Option("--chunk-size", type=int, default=50, help=HELP_CHUNK_SIZE),
            Option("--splitter", type=str, default="fixed", help=HELP_SPLITTER),
            Option("--first-n", type=int, help=HELP_FIRST_N),
            Option("--delay", type=float, default=1, help=HELP_DELAY),
            Option("-p", "--path", type=str, default=DEFAULT_PATH, help=HELP_PATH),
        ],
        run=lambda config: transmitters.run(**vars(config)),
    )

    socket_listener_cli = CLI(
        name=NAME_TPL.format(version=__version__),
        description=DESCRIPTION,
        version=__version__,
        examples=[
            "socket-listener -h",
            "socket-listener receiver --pubsub",
            "socket-listener transmitter --path myfile.txt",
        ],
        options=[
            Option("--protocol", type=str, default=DEFAULT_PROTOCOL, help=HELP_PROTOCOL),
            Option("--host", type=str, default="0.0.0.0", help=HELP_HOST),
            Option("--port", type=int, default=10110, help=HELP_PORT),
            Option("--daemon-thread", type=bool, default=False, help=HELP_DAEMON_THREAD),
        ],
        subcommands=[receiver_cmd, transmitter_cmd],
        logger_config=LoggerConfig(
            warning_level=[
                "google.cloud.pubsub_v1.publisher",
                "urllib3.connectionpool",
                "google.auth.transport.requests",
            ]
        ),
    )

    return socket_listener_cli.execute(args)


def main():
    cli(sys.argv[1:])


if __name__ == "__main__":
    main()
