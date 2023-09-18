"""
AIS Listener

Listens on a UDP port and writes received NMEA messages to sharded files in GCS
"""

import argparse
import os
from util.argparse import valid_date
from util.argparse import pretty_print_args
from util.argparse import setup_logging
from pipeline import Pipeline
import logging

PIPELINE_VERSION = '0.0.2'
PIPELINE_NAME = 'AIS Listener'
PIPELINE_DESCRIPTION = 'A UDP listener that receives NMEA-encoded AIS messages via UDP and writes them to sharded files in GCS'

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
server_args = subparsers.add_parser('server', help="listen to UDP")
client_args = subparsers.add_parser('client', help="Send lines from a file over UDP")

server_args.add_argument('--udp-port-range', type=int, nargs=2,
                         help='UDP port range to listen (default: %(default)s)',
                         default=[10110, 10110])
server_args.add_argument('--buffer-size', type=int,
                         help='size in bytes for the internal buffer'
                              '(default: %(default)s)',
                         default=4096)
server_args.add_argument('--gcs-dir', type=str,
                         help='GCS directory to write nmea shard files'
                              '(default: %(default)s)',
                         default='gs://scratch-paul-ttl100/ais-listener/')
server_args.add_argument('--source', type=str,
                         help='Source name to apply to all received NMEA.  If source-ip-map is specified, '
                              'then this value will be applied to messages received from any IP that is not '
                              'in the mapping file.'
                              '(default: %(default)s)',
                         default='ais-listener')
server_args.add_argument('--source-port-map', type=str,
                         help='File to read to get mapping of listening ports to source names'
                              '(default: %(default)s)',
                         default='sample/sources.yaml')
server_args.add_argument('--shard-interval', type=int,
                         help='Maximum interval in seconds between the first line and last line written to a '
                              'single shard file'
                              '(default: %(default)s)',
                         default=300)

client_args.add_argument('--server-ip', type=str,
                         help='IP address of server to send to (default: %(default)s)',
                         default="localhost")
client_args.add_argument('--udp-port', type=int,
                         help='UDP port to send to (default: %(default)s)',
                         default=10110)
client_args.add_argument('--filename', type=str,
                         help='name of file to read from (default: %(default)s)',
                         default="sample/nmea.txt")
client_args.add_argument('--delay', type=float,
                         help='Delay in seconds between messages (default: %(default)s)',
                         default=1)

def expand_udp_port_range():
    min_ports = 1
    max_ports = 10
    first, last = args.udp_port_range
    port_list = list(range(first, last + 1))
    num_ports = len(port_list)
    if  not(min_ports <= num_ports <= max_ports):
        parser.error(f"invalid udp_port_range containing {num_ports} ports. Must contain between {min_ports} and {max_ports} ports")
    return port_list


if __name__ == '__main__':
    args = parser.parse_args()
    log = setup_logging(args.verbosity)
    args.udp_port_list = expand_udp_port_range() if args.operation == 'server' else []

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
