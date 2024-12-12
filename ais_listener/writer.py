import gzip
import logging
import time
import uuid
from datetime import datetime

from cloudpathlib import GSClient, GSPath
from cloudpathlib.enums import FileCacheMode


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
