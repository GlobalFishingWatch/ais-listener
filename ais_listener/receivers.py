"""Classes for continuous socket data reception and persistence.

This module provides a base class for "receiver" objects and also concrete implementations.
These objects support the continuous data reception from network sockets and publication
to the configured data destinations or sinks.
"""

import math
import socket
import logging

import socketserver
import multiprocessing

from typing import Generator
from abc import ABC, abstractmethod

from retry.api import retry_call

from .packet import Packet
from .handlers import PacketHandler, UDPRequestHandler

logger = logging.getLogger(__name__)

multiprocessing.set_start_method('spawn', force=True)  # Otherwise deadlock can happen.


def run(config_file=None, *args, **kwargs):
    try:
        receiver = create(*args, **kwargs)
    except NotImplementedError as e:
        logger.error(e)
        return

    receiver.start()


def create(protocol, **kwargs):
    receivers = {
        "UDP": UDPSocketReceiver,
        "TCP_client": ClientTCPSocketReceiver,
    }

    if protocol not in receivers:
        raise NotImplementedError(f"Receiver for protocol '{protocol}' not implemented.")

    return receivers[protocol](**kwargs)


class SocketReceiver(ABC):
    """Base class for socket data reception.

    A socket receiver object can be implemented as server or as a client, as needed.
    In the case of servers, we leverage the socketserver module from the standard library.

    Args:
        host: Use this host (server) or connect to this host (client).
        port: The port to use.
        source_name: Name of the provider. Used only as metadata.
        max_packet_size: Maximum size in bytes for socket packets.
        max_retries: Maximum number of retries when a connection fails.
        max_retry_delay: Maximum delay between retries when a connection fails.
        init_retry_delay: Initial delay between retries when a connection fails.
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 10110,
        source_name: str = "Unknown",
        max_packet_size: int = 4096,
        max_retries: int = math.inf,
        max_retry_delay: float = 60,
        init_retry_delay: float = 1,
    ):
        self._host = host
        self._port = port
        self._source_name = source_name
        self._max_packet_size = max_packet_size
        self._max_retries = max_retries
        self._max_retry_delay = max_retry_delay
        self._init_retry_delay = init_retry_delay

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

        self._server = socketserver.ThreadingUDPServer((self._host, self._port), UDPRequestHandler)
        self._server.max_packet_size = self._max_packet_size

    def start(self) -> None:
        logger.info(f"Listening {self.protocol} socket on port {self._port}...")

        with self._server:
            self._server.serve_forever(poll_interval=self._poll_interval)

    def shutdown(self):
        self._server.shutdown()


class ClientTCPSocketReceiver(SocketReceiver):
    """TCP socket receiver implemented as a client.

    This class uses multiprocessing to spawn two independent processes that:
    - Continuously reads packets from a socket and puts them in a shared Queue.
    - Continuously reads packets from the shared Queue and process them.
    """

    protocol = "TCP"

    def __init__(
        self,
        connect_string: str = None,
        socket_factory=socket.socket,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._connect_string = connect_string
        self._socket_factory = socket_factory

        self.__shutdown_request = False
        self._queue = multiprocessing.Queue()
        self._logger = multiprocessing.get_logger()

    def start(self) -> None:
        logger.info(f"Connecting via {self.protocol} to {self.address}...")
        listen_process = multiprocessing.Process(target=type(self)._read_from_socket, args=(self,))
        listen_process.daemon = True
        listen_process.start()

        try:
            while not self.__shutdown_request:
                if self.__shutdown_request or not listen_process.is_alive():
                    break

                for packet in self._read_from_queue():
                    PacketHandler().handle_packet(packet)
        finally:
            self.__shutdown_request = False
            listen_process.terminate()
            listen_process.join()

    def shutdown(self):
        self.__shutdown_request = True

    def _read_from_socket(self) -> None:
        while True:
            try:
                logger.info("Getting socket connection...")
                sock = self._get_socket_with_retry()
            except ConnectionError as e:
                logger.error(f"Connection error: {e}. Max. retries exceeded.")
                self.shutdown()
                break

            logger.info("Enqueuing packets...")
            self._enqueue_packets(sock)
            sock.close()

    def _read_from_queue(self, n: int = 1000) -> Generator:
        remaining_packets = n
        while remaining_packets:
            try:
                packet = self._queue.get_nowait()
                if not packet.empty:
                    yield packet
                    remaining_packets -= 1
            except multiprocessing.queues.Empty:
                remaining_packets = 0

    def _get_socket_with_retry(self):
        return retry_call(
            self._get_socket,
            exceptions=ConnectionError,
            logger=self._logger,
            backoff=2,
            delay=self._init_retry_delay,
            max_delay=self._max_retry_delay,
            tries=self._max_retries + 1,
        )

    def _get_socket(self):
        """If connect() fails, the state of the socket is unspecified.
        Conforming applications should close the file descriptor and
        create a new socket before attempting to reconnect.
        https://man7.org/linux/man-pages/man3/connect.3p.html#APPLICATION_USAGE
        """

        sock = self._socket_factory(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        sock.settimeout(60)
        sock.connect(self.host_and_port)

        if self._connect_string:
            sock.send(self._connect_string.encode())

        return sock

    def _enqueue_packets(self, sock):
        try:
            while True:
                self._enqueue_packet(sock)
        except (ConnectionResetError, socket.timeout) as e:
            logger.warning(f"Connection closed: {e} Re-connecting...")

    def _enqueue_packet(self, sock):
        data = sock.recv(self._max_packet_size)
        packet = Packet(data, self.protocol, self._host, self._port)
        self._queue.put_nowait(packet)
