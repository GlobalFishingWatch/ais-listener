"""
TODO: Edit this
[Example pipeline]

Replace this with a description of what your pipeline does
"""

import argparse
import os
from util.argparse import valid_date
from util.argparse import pretty_print_args
from util.argparse import setup_logging
from pipeline import Pipeline
import logging

PIPELINE_VERSION = '0.0.1'
PIPELINE_NAME = 'AIS Listener'
PIPELINE_DESCRIPTION = 'A UDP listener that receives NMEA-encoded AIS messages via UDP and publishes them to pubsub'

# Some optional git parameters provided as environment variables.  Used for logging.
COMMIT_SHA = os.getenv('COMMIT_SHA', '')
COMMIT_BRANCH = os.getenv('COMMIT_BRANCH', '')
COMMIT_REPO = os.getenv('COMMIT_REPO', '')


parser = argparse.ArgumentParser(description=f'{PIPELINE_NAME} {PIPELINE_VERSION} - {PIPELINE_DESCRIPTION}')

### Common arguments
parser.add_argument('--test', action='store_true',
                    help='Test mode - print query and exit', default=False)

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

server_args.add_argument('--udp_port', type=int,
                         help='UDP port to listen (default: %(default)s)',
                         default=10110)
server_args.add_argument('--buffer_size', type=int,
                         help='size in bytes for the internal buffer'
                              '(default: %(default)s)',
                         default=1024)
server_args.add_argument('--gcs_dir', type=str,
                         help='GCS directory to write nmea shard files'
                              '(default: %(default)s)',
                         default='gs://scratch-paul-ttl100/ais-listener/')
server_args.add_argument('--source', type=str,
                         help='Source name to apply to all received NMEA'
                              '(default: %(default)s)',
                         default='ais-listener')
server_args.add_argument('--shard_interval', type=int,
                         help='Maximum interval in seconds between the first line and last line written to a '
                              'single shard file'
                              '(default: %(default)s)',
                         default=600)

client_args.add_argument('--server_ip', type=str,
                         help='IP address of server to send to (default: %(default)s)',
                         default="localhost")
client_args.add_argument('--udp_port', type=int,
                         help='UDP port to send to (default: %(default)s)',
                         default=10110)
client_args.add_argument('--filename', type=str,
                         help='name of file to read from (default: %(default)s)',
                         default="sample/nmea.txt")
client_args.add_argument('--delay', type=float,
                         help='Delay in seconds between messages (default: %(default)s)',
                         default=1)


args = parser.parse_args()
log = setup_logging(args.verbosity)

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

if __name__ == '__main__':
    result = pipeline.run()

    # exit code=0 indicates success.  Any other value indicates a failure
    exit_code = 0 if result else 1
    exit(exit_code)
