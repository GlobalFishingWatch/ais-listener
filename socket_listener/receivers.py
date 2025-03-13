"""Classes for continuous socket data reception and persistence.

This module provides a base class for "receiver" objects and also concrete implementations.
These objects support the continuous data reception from network sockets and publication
to the configured data destinations or sinks.
"""

import logging
import threading
import socketserver

from abc import ABC, abstractmethod
from functools import cached_property

from .handlers import UDPRequestHandler
from .sinks import create_sink
from .thread_monitor import ThreadMonitor


logger = logging.getLogger(__name__)


def run(
    *args,
    enable_pubsub: bool = False,
    project_id: str = None,
    topic_id: str = None,
    daemon_thread: bool = False,
    **kwargs,
):
    """Runs a socket receiver service inside a separate thread.

    Args:
        *args: Positional arguments for socket receiver constructor.
        enable_pubsub: Enables publication to Google Pub/Sub service.
        project_id: GCP project id.
        topic_id: Google Pub/Sub topic id.
        daemon_thread: If true, makes the thread daemonic.
        **kwargs: Keyword arguments for socket receiver constructor.

    Returns:
        A tuple (receiver, thread).
    """
    sinks = []
    if enable_pubsub:
        sinks.append(dict(name="google_pubsub", project_id=project_id, topic_id=topic_id))

    try:
        receiver = create(*args, **kwargs, sinks=sinks)
    except NotImplementedError as e:
        logger.error(e)
        return

    thread = threading.Thread(target=receiver.start)
    thread.daemon = daemon_thread
    thread.start()

    return receiver, thread


def create(protocol="UDP", *args, **kwargs) -> 'SocketReceiver':
    receivers = {
        "UDP": UDPSocketReceiver,
    }

    if protocol not in receivers:
        raise NotImplementedError(f"Receiver for protocol '{protocol}' not implemented.")

    return receivers[protocol].build(*args, **kwargs)


class SocketReceiver(ABC):
    """Base class for socket data reception.

    A socket receiver object implemented using
    We leverage the socketserver module from the standard library.

    Args:
        host: The IP address to use.
        port: The port to use.
        source_name: Name of the provider. Used only for metadata.
        max_packet_size: The maximum amount of data to be received at once.
        sinks: list of sinks in which to publish incoming packets.
    """
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 10110,
        source_name: str = "Unknown",
        max_packet_size: int = 4096,
        sinks: list = None,
        monitor_delay: int = 2
    ) -> None:
        self._host = host
        self._port = port
        self._source_name = source_name
        self._max_packet_size = max_packet_size
        self._sinks = sinks

        self._thread_monitor = ThreadMonitor(delay=monitor_delay)

    @classmethod
    def build(cls, sinks=(), *args, **kwargs) -> 'SocketReceiver':
        """Builds a socket receiver object."""
        sinks = [create_sink(**config) for config in sinks]

        sinks_str = ", ".join([s.name for s in sinks])
        logger.info(f"{len(sinks)} sink(s) configured ({sinks_str}).")

        return cls(*args, **kwargs, sinks=sinks)

    @cached_property
    def address(self) -> str:
        """Unified string version of the host and port properties."""
        return f"{self._host}:{self._port}"

    @cached_property
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
        self._server.source_name = self._source_name
        self._server.sinks = self._sinks

    def start(self) -> None:
        logger.info(f"Listening {self.protocol} socket on {self.address}...")
        self._thread_monitor.start()
        with self._server:
            self._server.serve_forever(poll_interval=self._poll_interval)

    def shutdown(self):
        self._server.shutdown()
        self._thread_monitor.stop()
