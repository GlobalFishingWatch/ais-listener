import time
import queue
import socket
import logging
import multiprocessing


logger = logging.getLogger(__name__)


class MessageStream(object):
    def __init__(
        self,
        source,
        hostname="0.0.0.0",
        port=10110,
        bufsize=4096,
        timeout=10,
        connect_string=None,
    ):
        self.source = source
        self.hostname = hostname
        self.port = port
        self.bufsize = bufsize
        self.queue = multiprocessing.Queue()
        self.use_station_id = False
        self.timeout = timeout
        self.connect_string = connect_string

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
                # logger.debug(f'No messages received for {self.timeout} seconds')
                # empty = True

    def read_messages(self):
        yield from self.read_from_queue()

    def handle(self):
        messages = self.read_messages()
        lines = self._extract_lines(messages)

        size = len(list(lines))
        if size > 0:
            logger.info(f"Received {size} messages.")

    def run(self):
        logger.info(f"listening on {self.hostname}:{self.port}")
        listen_process = multiprocessing.Process(target=UdpStream.read_from_port, args=(self,))
        listen_process.daemon = True
        listen_process.start()

        return [listen_process]

    def _extract_lines(self, messages):
        for message, addr, timestamp, port in messages:
            lines = (line.strip() for line in message.split('\n'))
            lines = (line for line in lines if line)
            for line in lines:
                yield line


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
            except ConnectionRefusedError:
                logger.error(
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
                    logger.info(f"Server {self.hostname}:{self.port} TCP connection closed")
                    break

            # 3. proper closure
            sock.close()

    def run(self):
        logger.info(f"Connecting via TCP {self.hostname}:{self.port}")
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
        logger.info(f"Listening on UDP {self.hostname}:{self.port}")
        listen_process = multiprocessing.Process(target=UdpStream.read_from_port, args=(self,))
        listen_process.daemon = True
        listen_process.start()

        return [listen_process]
