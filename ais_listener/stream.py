import multiprocessing
import queue
import socket
import time

from ais_listener.writer import GCSShardWriter
from ais_listener.utils.nmea import format_nmea


class MessageStream(object):
    def __init__(
        self,
        log,
        gcs_dir,
        source,
        hostname="0.0.0.0",
        port=10110,
        bufsize=4096,
        timeout=10,
        shard_interval=300,
        connect_string=None,
    ):
        self.log = log
        self.gcs_dir = gcs_dir
        self.source = source
        self.hostname = hostname
        self.port = port
        self.bufsize = bufsize
        self.queue = multiprocessing.Queue()
        self.max_time_window = 500
        self.max_message_window = 1000
        self.use_station_id = False
        self.timeout = timeout
        self.shard_interval = shard_interval
        self.connect_string = connect_string
        self.writer = GCSShardWriter(
            gcs_dir=self.gcs_dir, file_prefix=self.source, shard_interval=self.shard_interval
        )

    def read_from_port(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP
        sock.bind((self.hostname, self.port))
        while True:
            data, addr = sock.recvfrom(self.bufsize)
            message = data, addr, time.time(), self.port
            self.queue.put_nowait(message)

    def read_from_queue(self, max_messages=1000):
        messages_remaining = max_messages
        while messages_remaining:
            try:
                # data, addr, timestamp, port = self.queue.get(timeout=self.timeout)
                data, addr, timestamp, port = self.queue.get_nowait()
                data = data.decode("utf-8").strip()
                if data:
                    yield data, addr, timestamp, port
                    messages_remaining -= 1
            except queue.Empty:
                messages_remaining = 0
                # self.log.debug(f'No messages received for {self.timeout} seconds')
                # empty = True

    def read_messages(self):
        yield from self.read_from_queue()

    def write_to_file(self):
        messages = self.read_messages()
        lines = format_nmea(messages, self.source)
        self.writer.write_lines(lines)
        if self.writer.is_stale():
            self.writer.close()  # close this shard.   A new one will be opened on the next write

    def run(self):
        self.log.info(f"listening on {self.hostname}:{self.port}")
        listen_process = multiprocessing.Process(target=UdpStream.read_from_port, args=(self,))
        listen_process.daemon = True
        listen_process.start()

        return [listen_process]


class TcpStream(MessageStream):
    def read_from_port(self):
        initial_retry_delay = 1
        max_retry_delay = 60

        retry_delay = initial_retry_delay
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                sock.settimeout(60)
                sock.connect((self.hostname, self.port))
                # print(sock.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE))
            except ConnectionRefusedError:
                self.log.error(
                    f"Server {self.hostname}:{self.port} refused TCP connection. retrying"
                )
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
                continue

            if self.connect_string:
                sock.send(self.connect_string.encode())

            retry_delay = initial_retry_delay

            # 2. communication routine
            while True:
                try:
                    data = sock.recv(self.bufsize)
                    message = data, self.hostname, time.time(), self.port
                    self.queue.put_nowait(message)

                except (ConnectionResetError, socket.timeout):
                    print(f"Server {self.hostname}:{self.port} TCP connection closed")
                    break

            # 3. proper closure
            # sock.shutdown(socket.SHUT_RDWR)
            sock.close()

    def run(self):
        self.log.info(f"Connecting via TCP {self.hostname}:{self.port}")
        listen_process = multiprocessing.Process(target=TcpStream.read_from_port, args=(self,))
        listen_process.daemon = True
        listen_process.start()

        return [listen_process]


class UdpStream(MessageStream):
    def read_from_port(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP
        sock.bind((self.hostname, self.port))
        while True:
            data, addr = sock.recvfrom(self.bufsize)
            message = data, addr[0], time.time(), self.port
            self.queue.put_nowait(message)

    def run(self):
        self.log.info(f"Listening on UDP {self.hostname}:{self.port}")
        listen_process = multiprocessing.Process(target=UdpStream.read_from_port, args=(self,))
        listen_process.daemon = True
        listen_process.start()

        return [listen_process]
