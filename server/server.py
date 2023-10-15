import logging
import multiprocessing
import queue
import socket
import time
from datetime import datetime
from cloudpathlib import GSPath
from cloudpathlib import GSClient
from cloudpathlib.enums import FileCacheMode
import uuid
import gzip

from util.nmea import format_nmea


class UdpServer(object):
    def __init__(self, log, gcs_dir, source, hostname="0.0.0.0", port=10110, bufsize=4096, timeout=10,
                 shard_interval=300):
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
        self.writer = GCSShardWriter(
            gcs_dir=self.gcs_dir,
            file_prefix=self.source,
            shard_interval=self.shard_interval
        )

    def read_from_port(self):
        sock = socket.socket(socket.AF_INET,        # Internet
                             socket.SOCK_DGRAM)     # UDP
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
                data = data.decode('utf-8').strip()
                if data:
                    yield data, addr[0], timestamp, port
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
        self.log.info(f'listening on {self.hostname}:{self.port}')
        listen_process = multiprocessing.Process(target=UdpServer.read_from_port, args=(self,))
        listen_process.daemon = True
        listen_process.start()

        return [listen_process]


class GCSShardWriter(object):
    def __init__(self, gcs_dir, file_prefix, shard_interval=600, log=None):
        self.gcs_dir = gcs_dir
        self.file_prefix = file_prefix
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

        filename = f'{self.file_prefix}_{dt}_{tm}_{hash}.nmea.gz'
        client = GSClient(file_cache_mode=FileCacheMode.close_file)
        f = GSPath(self.gcs_dir, client=client) / dt / filename
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
