"""
Pipeline operational logic.  All the real work gets done here
"""

import logging
import socket
import time
from receiver.stream import TcpStream, UdpStream

from util.sources import load_config_file


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


    def run_receiver(self):
        processes = []
        receivers = []
        config = load_config_file(self.args.config_file)
        for source in config['sources']:
            if source['protocol'] == 'UDP':
                receiver = UdpStream(log=self.log,
                                   gcs_dir=self.args.gcs_dir,
                                   source=source['source'],
                                   port=source['port'],
                                   bufsize=self.args.buffer_size,
                                   shard_interval=self.args.shard_interval)
                processes.extend(receiver.run())
                receivers.append(receiver)
            elif source['protocol'] == 'TCP':
                receiver = TcpStream(log=self.log,
                                   gcs_dir=self.args.gcs_dir,
                                   source=source['source'],
                                   hostname=source['host'],
                                   port=source['port'],
                                   bufsize=self.args.buffer_size,
                                   shard_interval=self.args.shard_interval,
                                   connect_string=source.get('connect_string'))
                processes.extend(receiver.run())
                receivers.append(receiver)
            else:
                raise RuntimeError(f'Invalid protocol for source {source["source"]}: {source["protocol"]}')

        # for port in self.args.udp_port_list:
        #
        #     source = source_port_map.get(port)
        #     if not source:
        #         source = f'{self.args.source}-{port}'
        #
        #     server = UdpServer(log=self.log,
        #                        gcs_dir=self.args.gcs_dir,
        #                        source=source,
        #                        port=port,
        #                        bufsize=self.args.buffer_size,
        #                        shard_interval=self.args.shard_interval)
        #     processes.extend(server.run())
        #     servers.append(server)
        while True:
            for receiver in receivers:
                receiver.write_to_file()

        # multiprocessing.connection.wait([p.sentinel for p in processes])

    def run_udp_transmitter(self):
        server_ip = self.args.receiver_ip
        port = self.args.port
        filename = self.args.filename
        delay = self.args.delay

        self.log.info(f'reading messages from {filename}')
        self.log.info(f'Sending UDP messages to {server_ip}:{port} every {delay} seconds')

        sock = socket.socket(socket.AF_INET,        # Internet
                             socket.SOCK_DGRAM)     # UDP

        with open(filename, 'r') as f:
            for line in f:
                nmea = line.strip()
                sock.sendto(nmea.encode('utf-8'), (server_ip, port))
                self.log.info(nmea)
                if delay:
                    time.sleep(delay)

    def run_tcp_transmitter(self):

        while True:
            # 1. Configure server socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('127.0.0.1', self.args.port))
            sock.listen(1)
            self.log.info("Waiting for receiver to connect...")
            connection, addr = sock.accept()
            connection.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            # print(connection.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE))
            self.log.info("...connected.")
            sock.close()

            # 2. communication routine
            while True:
                try:
                    with open(self.args.filename, 'r') as f:
                        for line in f:
                            nmea = line.strip()
                            connection.send(nmea.encode('utf-8') + b'\n')
                            self.log.info(nmea)
                            if self.args.delay:
                                time.sleep(self.args.delay)
                            # sentence = connectionSocket.recv(1024).decode()

                except (ConnectionResetError, BrokenPipeError) as e:
                    self.log.info("Client connection closed")
                    break

            # 3. proper closure
            connection.close()
            print("connection closed.")

    def run_transmitter(self):
        if self.args.protocol == 'UDP':
            self.run_udp_transmitter()
        elif self.args.protocol == 'TCP':
            self.run_tcp_transmitter()
        else:
            raise RuntimeError(f'Invalid protocol: {self.args.protocol}')


    def run(self):
        if self.args.operation == 'receiver':
            return self.run_receiver()
        if self.args.operation == 'transmitter':
            return self.run_transmitter()
        else:
            raise RuntimeError(f'Invalid operation: {self.args.operation}')
