"""Module that encapuslates socket data transmitters."""

import time
import socket
import logging
import threading

from typing import Generator
from abc import ABC, abstractmethod
from functools import cached_property
from itertools import islice, batched

logger = logging.getLogger(__name__)


def run(filepath, *args, thread=False, **kwargs):
    try:
        transmitter = create(*args, **kwargs)
    except NotImplementedError as e:
        logger.error(e)
        return

    if thread:
        thread = threading.Thread(target=transmitter.start, args=[filepath])
        thread.daemon = True
        thread.start()

        return transmitter, thread

    transmitter.start(filepath)
    return transmitter, None


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
            path: Path to the file containing the data to be sent.
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
        logger.info(
            "Sending chunks of {} messages using UDP to {} every {} seconds".format(
                self._chunk_size, self.address, self._delay
            )
        )

        messages = islice(self._read_messages(path), 0, self._first_n)
        chunks = batched(messages, self._chunk_size)

        for chunk in chunks:
            self._send_messages(chunk)
            if self.__shutdown_request:
                break

    def _read_messages(self, path) -> Generator:
        logger.info(f"Reading messages from {path}.")
        with open(path, "r") as f:
            for line in f:
                yield line.strip()

    def _send_messages(self, messages: list[bytes]):
        data = "\n".join(messages).encode("utf-8")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((self._host, self._port))
        sock.send(data)
        sock.close()

        logger.info(f"Finished sending {len(messages)} messages to {self.address}.")
        logger.debug(f"Data sent: {data}")
        time.sleep(self._delay)

    def shutdown(self):
        self.__shutdown_request = True
