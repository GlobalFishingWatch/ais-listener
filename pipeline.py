"""
Pipeline operational logic.  All the real work gets done here
"""

import logging
import socket
import time
from server.server import UdpServer
from server.server import GCSShardWriter
from util.nmea import format_nmea
from util.sources import load_source_ip_map

class Pipeline:
    def __init__(self, args):
        self.log = logging.getLogger('main')
        self.dry_run = args.test
        self.args = args

    @property
    def is_test_mode(self):
        return self.args.test

    @property
    def params(self):
        """
        Gets a dict version of self.args
        :return: dict
        """
        return vars(self.args)


    def run_server(self):
        source_ip_map = load_source_ip_map(self.args.source_ip_map, default_source=self.args.source)
        server = UdpServer(log=self.log, ports=self.args.udp_port_list, bufsize=self.args.buffer_size)
        server.run()
        with GCSShardWriter(
                gcs_dir=self.args.gcs_dir,
                file_suffix=self.args.source,
                shard_interval=self.args.shard_interval
                ) as writer:
            while True:
                messages = server.read_messages()
                lines = format_nmea(messages, source_ip_map)
                writer.write_lines(lines)
                if writer.is_stale():
                    writer.close()

    def run_client(self):
        server_ip = self.args.server_ip
        port = self.args.udp_port
        filename = self.args.filename
        delay = self.args.delay

        self.log.info(f'reading messages from {filename}')
        self.log.info(f'Sending messages to {server_ip}:{port} every {delay} seconds')

        sock = socket.socket(socket.AF_INET,        # Internet
                             socket.SOCK_DGRAM)     # UDP

        with open(filename, 'r') as f:
            for line in f:
                nmea = line.strip()
                sock.sendto(nmea.encode('utf-8'), (server_ip, port))
                self.log.info(nmea)
                if delay:
                    time.sleep(delay)

    def run(self):
        if self.args.operation == 'server':
            return self.run_server()
        if self.args.operation == 'client':
            return self.run_client()
        else:
            raise RuntimeError(f'Invalid operation: {self.args.operation}')

        return False    # should not be able to get here, but just in case, return failure
