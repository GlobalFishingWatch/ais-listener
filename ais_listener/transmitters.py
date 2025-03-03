"""Module that encapuslates socket data transmitters."""

import time
import socket
import logging
import socketserver

from typing import Generator
from abc import ABC, abstractmethod

from .handlers import TCPRequestHandler

logger = logging.getLogger(__name__)


def run(filepath, *args, **kwargs):
    try:
        transmitter = create(*args, **kwargs)
    except NotImplementedError as e:
        logger.error(e)
        return

    transmitter.start(filepath)


def create(protocol, **kwargs):
    transmitters = {
        "UDP": UDPSocketTransmitter,
        "TCP": TCPSocketTransmitter,
    }

    if protocol not in transmitters:
        raise NotImplementedError(f"Transmitter for protocol {protocol} not implemented.")

    return transmitters[protocol](**kwargs)


class SocketTransmitter(ABC):
    """Base class for socket data transmission."""

    def __init__(self, host: str, port: int, delay: float = 1, max_chunk_size: int = 50):
        self._host = host
        self._port = port
        self._delay = delay
        self._max_chunk_size = max_chunk_size

        self._address = f"{self._host}:{self._port}"
        self.__shutdown_request = False

    @abstractmethod
    def start(self, path: str):
        """Starts the socket transmitter."""

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
            "Sending {} messages using UDP to {} every {} seconds".format(
                self._max_chunk_size, self._address, self._delay
            )
        )

        messages = self._read_messages(path)

        while not self.__shutdown_request:
            chunk = []
            for m in messages:
                chunk.append(m)
                # logger.info(self.__shutdown_request)
                if self.__shutdown_request:
                    break

                if len(chunk) >= self._max_chunk_size:
                    self._send_messages(chunk)
                    chunk = []

    def _read_messages(self, path) -> Generator:
        logger.info(f"Reading messages from {path}.")
        with open(path, "r") as f:
            for line in f:
                yield line.strip().encode("utf-8")

    def _send_messages(self, messages: list[bytes]):
        data = b"\n".join(messages)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((self._host, self._port))
        sock.send(data)
        sock.close()

        logger.info(f"Finished sending {len(messages)} messages to {self._address}.")
        logger.debug(f"Data sent: {data}")
        time.sleep(self._delay)

    def shutdown(self):
        self.__shutdown_request = True


class TCPSocketTransmitter(SocketTransmitter):
    """A socket TCP transmitter implemented as a socket server."""

    LOCALHOST = "127.0.0.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._server = socketserver.TCPServer((self._host, self._port), TCPRequestHandler)
        self._server.max_chunk_size = self._max_chunk_size
        self._server.allow_reuse_addres = True
        self._server.delay = self._delay

    def start(self, path: str) -> None:
        logger.info("Listening for TCP requests on {}".format(self._server.server_address))
        with self._server as server:
            # server.request_queue_size = 1
            server.data_path = path
            server.serve_forever()

    def shutdown(self):
        self._server.shutdown()
