"""Module that encapuslates socket data transmitters."""

import time
import math
import gzip
import socket
import logging
import threading

from pathlib import Path
from typing import Generator, Iterable, Any
from abc import ABC, abstractmethod
from functools import cached_property
from itertools import islice

from rich.progress import track

from .utils import chunked_it

logger = logging.getLogger(__name__)


def open_file(path: Path, mode: str = 'rt', **kwargs: Any):
    """Open a file using gzip.open if it ends with .gz, otherwise use open.

    Args:
        path: A pathlib.Path object pointing to the file.
        mode: Mode to open the file. Use 'rt' or 'rb' for gzip files.
        **kwargs: Additional arguments passed to open or gzip.open.

    Returns:
        file object: An open file object.
    """
    opener = gzip.open if path.suffix == '.gz' else open
    return opener(path, mode, **kwargs)


def run(path, *args, daemon_thread=False, **kwargs):
    """Runs a socket transmitter service inside a separate thread.

    Args:
        path: the path to the file or folder containing the data to be sent.
        *args: Positional arguments for socket transmitter constructor.
        daemon_thread: If true, makes the thread daemonic.
        **kwargs: Keyword arguments for socket transmitter constructor.

    Returns:
        A tuple (transmitter, thread).
    """
    try:
        transmitter = create(*args, **kwargs)
    except NotImplementedError as e:
        logger.error(e)
        return

    thread = threading.Thread(target=transmitter.start, args=[path])
    thread.daemon = daemon_thread
    thread.start()

    return transmitter, thread


def create(protocol="UDP", **kwargs):
    transmitters = {
        "UDP": UDPSocketTransmitter,
    }

    if protocol not in transmitters:
        raise NotImplementedError(f"Transmitter for protocol {protocol} not implemented.")

    return transmitters[protocol](**kwargs)


class SocketTransmitter(ABC):
    """Base class for socket data transmission.

    Args:
        host: IP to connect to.
        port: Port to connect to.
        delay: Delay in seconds between packet transmissions.
        chunk_size: Amount of messages to be sent in a single packet.
        first_n: If passed, only send this amount of messages of the file and then stop.
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 10110,
        delay: float = 1,
        chunk_size: int = 50,
        first_n: int = None
    ):
        self._host = host
        self._port = port
        self._delay = delay
        self._chunk_size = chunk_size
        self._first_n = first_n

    @abstractmethod
    def start(self, path: str):
        """Starts the socket transmitter.

        Args:
            path: Path to the file or folder containing the data to be sent.
        """

    @cached_property
    def address(self):
        """Unified string version of the host and port properties."""
        return f"{self._host}:{self._port}"

    @abstractmethod
    def shutdown(self):
        """Terminates the server."""


class UDPSocketTransmitter(SocketTransmitter):
    """A socket UDP transmitter implemented as a socket client."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__shutdown_request = False

    def start(self, path: str) -> None:
        logger.info(f"Reading messages from {path}.")
        logger.info(
            "Sending chunks of {} messages using UDP to {} every {} seconds".format(
                self._chunk_size, self.address, self._delay
            )
        )

        path = Path(path)

        if path.is_dir():
            paths = sorted(path.iterdir())
        else:
            paths = [path]

        for i, p in enumerate(paths, 1):
            if p.is_dir():
                logger.warning(f"Found subfolder: {p.relative_to(p.parent.parent)}. Ignoring...")
                continue

            logger.info(f"Processing file {i} of {len(paths)}...")
            self._process_file(p)

    def _process_file(self, path):
        chunk_count = math.ceil(self._get_file_line_count(path) / self._chunk_size)
        messages = islice(self._read_messages(path), 0, self._first_n)
        chunks = chunked_it(messages, self._chunk_size)

        for chunk in track(chunks, total=chunk_count):
            self._send_messages(chunk)
            if self.__shutdown_request:
                break

    def _get_file_line_count(self, path) -> Generator:
        count = 0
        with open_file(path, "rt") as f:
            for line in f:
                count += 1

        return count

    def _read_messages(self, path) -> Generator:
        with open_file(path, "rt") as f:
            for line in f:
                yield line.strip()

    def _send_messages(self, messages: Iterable[bytes]):
        messages_lst = list(messages)
        data = "\n".join(messages_lst).encode("utf-8")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((self._host, self._port))
        sock.send(data)
        sock.close()

        logger.debug(f"Data sent: {data}")
        time.sleep(self._delay)

    def shutdown(self):
        self.__shutdown_request = True
