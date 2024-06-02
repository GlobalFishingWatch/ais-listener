"""
AIS Listener

Listens on a UDP port and writes received NMEA messages to sharded files in GCS
"""

import argparse
import os
from util.argparse import pretty_print_args
from util.argparse import setup_logging
from pipeline import Pipeline

PIPELINE_VERSION = '0.1.0'
PIPELINE_NAME = 'AIS Listener'
PIPELINE_DESCRIPTION = 'A TCP/UDP service that receives NMEA-encoded AIS messages via UDP or TCP ' \
                       'and writes them to sharded files in GCS'

# Some optional git parameters provided as environment variables.  Used for logging.
COMMIT_SHA = os.getenv('COMMIT_SHA', '')
COMMIT_BRANCH = os.getenv('COMMIT_BRANCH', '')
COMMIT_REPO = os.getenv('COMMIT_REPO', '')


parser = argparse.ArgumentParser(description=f'{PIPELINE_NAME} {PIPELINE_VERSION} - {PIPELINE_DESCRIPTION}')

### Common arguments
parser.add_argument('--test', action='store_true',
                    help='Test mode - this setting is currently ignored.  Use -v or -vv when testing', default=False)

parser.add_argument('-v', '--verbose',
                    action='count',
                    dest='verbosity',
                    default=0,
                    help="verbose output (repeat for increased verbosity)")

parser.add_argument('-q', '--quiet',
                    action='store_const',
                    const=-1,
                    default=0,
                    dest='verbosity',
                    help="quiet output (show errors only)")

parser.add_argument('--project', type=str,
                    help='GCP project id (default: %(default)s)',
                    default='world-fishing-827')


### operations
subparsers = parser.add_subparsers(dest='operation', required=True)
receiver_args = subparsers.add_parser('receiver', help="receive nmea lines from a TCP ot UDP transmitter")
transmitter_args = subparsers.add_parser('transmitter', help="Send lines from a file")

# receiver_args.add_argument('--udp-port-range', type=int, nargs=2,
#                          help='UDP port range to listen (default: %(default)s)',
#                          default=[10110, 10110])
receiver_args.add_argument('--buffer-size', type=int,
                         help='size in bytes for the internal buffer'
                              '(default: %(default)s)',
                         default=4096)
receiver_args.add_argument('--gcs-dir', type=str,
                         help='GCS directory to write nmea shard files'
                              '(default: %(default)s)',
                         default='gs://scratch-paul-ttl100/ais-listener/')
# receiver_args.add_argument('--default_source', type=str,
#                          help='Source name to apply to all received NMEA.  If source-map is specified, '
#                               'then this value will be applied to messages received by any UDP port that is not '
#                               'in the mapping file.'
#                               '(default: %(default)s)',
#                          default='ais-listener')
receiver_args.add_argument('--config_file', type=str,
                         help='File to read to get mapping of listening ports to source names'
                              '(default: %(default)s)',
                         default='sample/sources.yaml')
receiver_args.add_argument('--shard-interval', type=int,
                         help='Maximum interval in seconds between the first line and last line written to a '
                              'single shard file'
                              '(default: %(default)s)',
                         default=300)

transmitter_args.add_argument('--protocol', type=str,
                         help='UDP or TCP (default: %(default)s)',
                         default="UDP")
transmitter_args.add_argument('--receiver-ip', type=str,
                         help='For UDP, the IP address of receiver to send to (default: %(default)s)',
                         default="localhost")
transmitter_args.add_argument('--port', type=int,
                         help='UDP/TCP port (default: %(default)s)',
                         default=10110)
transmitter_args.add_argument('--filename', type=str,
                         help='Name of file to read from (default: %(default)s)',
                         default="sample/nmea.txt")
transmitter_args.add_argument('--delay', type=float,
                         help='Delay in seconds between messages (default: %(default)s)',
                         default=1)


# def expand_udp_port_range():
#     min_ports = 1
#     max_ports = 10
#     first, last = args.udp_port_range
#     port_list = list(range(first, last + 1))
#     num_ports = len(port_list)
#     if not(min_ports <= num_ports <= max_ports):
#         parser.error(f"invalid udp_port_range containing {num_ports} ports. "
#                      f"Must contain between {min_ports} and {max_ports} ports")
#     return port_list


if __name__ == '__main__':
    args = parser.parse_args()
    log = setup_logging(args.verbosity)
    # args.udp_port_list = expand_udp_port_range() if args.operation == 'receiver' else []

    args.COMMIT_SHA = COMMIT_SHA
    args.COMMIT_BRANCH = COMMIT_BRANCH
    args.COMMIT_REPO = COMMIT_REPO

    log.info(f'{PIPELINE_NAME} v{PIPELINE_VERSION}')
    log.info(f'{PIPELINE_DESCRIPTION}')
    log.info(pretty_print_args(args))

    args.PIPELINE_VERSION = PIPELINE_VERSION
    args.PIPELINE_NAME = PIPELINE_NAME
    args.PIPELINE_DESCRIPTION = PIPELINE_DESCRIPTION

    pipeline = Pipeline(args)

    result = pipeline.run()

    # exit code=0 indicates success.  Any other value indicates a failure
    exit_code = 0 if result else 1
    exit(exit_code)
