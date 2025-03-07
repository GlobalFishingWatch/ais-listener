"""Classes for continuous socket data reception and persistence.

This module provides a base class for "receiver" objects and also concrete implementations.
These objects support the continuous data reception from network sockets and publication
to the configured data destinations or sinks.
"""

import logging
import threading
import socketserver

from abc import ABC, abstractmethod

from .handlers import UDPRequestHandler

logger = logging.getLogger(__name__)


def run(*args, thread=False, **kwargs):
    try:
        receiver = create(*args, **kwargs)
    except NotImplementedError as e:
        logger.error(e)
        return

    if thread:
        thread = threading.Thread(target=receiver.start)
        thread.daemon = True
        thread.start()

        return receiver, thread

    receiver.start()
    return receiver, None


def create(protocol, **kwargs):
    receivers = {
        "UDP": UDPSocketReceiver,
    }

    if protocol not in receivers:
        raise NotImplementedError(f"Receiver for protocol '{protocol}' not implemented.")

    return receivers[protocol](**kwargs)


class SocketReceiver(ABC):
    """Base class for socket data reception.

    A socket receiver object implemented using
    We leverage the socketserver module from the standard library.

    Args:
        host: The IP address to use.
        port: The port to use.
        source_name: Name of the provider. Used only for metadata.
        max_packet_size: The maximum amount of data to be received at once.
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 10110,
        source_name: str = "Unknown",
        max_packet_size: int = 4096,
    ):
        self._host = host
        self._port = port
        self._source_name = source_name
        self._max_packet_size = max_packet_size

    @property
    def address(self) -> str:
        """Unified string version of the host and port properties."""
        return f"{self._host}:{self._port}"

    @property
    def host_and_port(self) -> tuple:
        """Tupled version of the host and port properties."""
        return (self._host, self._port)

    @abstractmethod
    def start(self) -> None:
        """Starts the socket receiver."""


class UDPSocketReceiver(SocketReceiver):
    """UDP socket receiver implemented as a server.

    This class uses socketserver.ThreadingUDPServer class from the standard library.
    """

    protocol = "UDP"

    def __init__(self, poll_interval: float = 0.5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._poll_interval = poll_interval

        self._server = socketserver.ThreadingUDPServer(self.host_and_port, UDPRequestHandler)
        self._server.max_packet_size = self._max_packet_size

    def start(self) -> None:
        logger.info(f"Listening {self.protocol} socket on {self.address}...")

        with self._server:
            self._server.serve_forever(poll_interval=self._poll_interval)

    def shutdown(self):
        self._server.shutdown()
