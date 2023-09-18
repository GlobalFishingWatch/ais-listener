import logging
import multiprocessing
import queue
import socket
import time
from datetime import datetime
from ais_tools.nmea import join_multipart_stream
from cloudpathlib import GSPath
import uuid
import gzip


class UdpServer(object):
    def __init__(self, log, hostname="0.0.0.0", ports=(10110,), bufsize=4096, timeout=10):
        self.log = log
        self.hostname = hostname
        self.ports = ports
        self.bufsize = bufsize
        self.queue = multiprocessing.Queue()
        self.max_time_window = 500
        self.max_message_window = 1000
        self.use_station_id = False
        self.timeout = timeout


    def read_from_port(self, port):
        sock = socket.socket(socket.AF_INET,        # Internet
                             socket.SOCK_DGRAM)     # UDP
        sock.bind((self.hostname, port))
        while True:
            data, addr = sock.recvfrom(self.bufsize)
            message = data, addr, time.time(), port
            self.queue.put_nowait(message)

    def read_from_queue(self):
        empty = False
        while not empty:
            try:
                data, addr, timestamp, port = self.queue.get(timeout=self.timeout)
                data = data.decode('utf-8').strip()
                if data:
                    yield data, addr[0], timestamp, port
            except queue.Empty:
                self.log.debug(f'No messages received for {self.timeout} seconds')
                empty = True

    def run(self):
        for port in self.ports:
            self.log.info(f'listening on {self.hostname}:{port}')
            process = multiprocessing.Process(target=UdpServer.read_from_port, args=(self, port))
            process.daemon = True
            process.start()

    def read_messages(self):
        yield from self.read_from_queue()


class GCSShardWriter(object):
    def __init__(self, gcs_dir, file_suffix, shard_interval=600, log=None):
        self.gcs_dir = gcs_dir
        self.file_suffix = file_suffix
        self.shard_interval = shard_interval
        self.log = log or logging.getLogger('main')

        self._file = None
        self._gz_file = None
        self._file_start_time = time.time()
        self._line_count = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._close()

    def _close(self):
        if self._file:
            self._gz_file.close()
            self._file.close()
            self.log.info(f'Wrote {self._line_count} lines')
        self._file = None
        self._gz_file = None
        self._line_count = 0

    def _open(self):
        if self._file:
            self._close()

        now = datetime.utcnow()
        dt = now.strftime('%Y%m%d')
        tm = now.strftime('%H%M%S')
        hash = uuid.uuid4()

        filename = f'{self.file_suffix}_{dt}_{tm}_{hash}.nmea.gz'
        f = GSPath(self.gcs_dir) / dt / filename
        self.log.info(f'Writing to {f.as_uri()}')
        self._file = f.open('wb')
        self._gz_file = gzip.GzipFile(mode='w', fileobj=self._file)
        self._file_start_time = time.time()
        self._line_count = 0

    def open(self):
        self._open()

    def close(self):
        self._close()

    def is_stale(self):
        file_active_interval = time.time() - self._file_start_time
        return self._file is None or file_active_interval > self.shard_interval

    def write_line(self, line):
        if self.is_stale():
            self._close()
            self._open()

        self._gz_file.write(line.encode('utf-8') + b'\n')
        self.log.debug(line)
        self._line_count += 1

    def write_lines(self, lines):
        for line in lines:
            self.write_line(line)
