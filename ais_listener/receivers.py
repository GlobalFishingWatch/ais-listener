"""Module that encapuslates socket data receivers."""

import time
import socket
import logging

import socketserver
import multiprocessing

from typing import Generator
from abc import ABC, abstractmethod

from .packet import Packet
from .handlers import PacketHandler, UDPRequestHandler

logger = logging.getLogger(__name__)


def run(protocol, config_file=None, **kwargs):
    receivers = {
        "udp": UDPSocketReceiver,
        "tcp_client": ClientTCPSocketReceiver,
    }

    if protocol not in receivers:
        raise NotImplementedError(f"Receiver for protocol '{protocol}' not implemented.")

    receiver = receivers[protocol](**kwargs)
    receiver.start()


class SocketReceiver(ABC):
    """Base class for socket data reception.

    Subclasses can implement receivers as servers or clients, as needed.
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 10110,
        max_packet_size: int = 4096,
        source_name: str = "Unknown",
    ):
        self._host = host
        self._port = port
        self._max_packet_size = max_packet_size
        self._source_name = source_name

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
    """UDP socket receiver implemented as a server."""

    protocol = "UDP"

    def start(self) -> None:
        logger.info(f"Listening {self.protocol} socket on port {self._port}...")

        with socketserver.UDPServer(self.host_and_port, UDPRequestHandler) as server:
            server.max_packet_size = self._max_packet_size
            server.serve_forever()


class ClientTCPSocketReceiver(SocketReceiver):
    """TCP socket receiver implemented as a client."""

    protocol = "TCP"

    def __init__(
        self,
        connect_string: str = None,
        init_retry_delay: float = 1,
        max_retry_delay: float = 60,
        *args,
        **kwargs,
    ):
        self._connect_string = connect_string
        self._queue = multiprocessing.Queue()
        self._init_retry_delay = init_retry_delay
        self._max_retry_delay = max_retry_delay

        super().__init__(*args, **kwargs)

    def start(self) -> None:
        logger.info(f"Connecting via {self.protocol} to {self.address}...")
        listen_process = multiprocessing.Process(target=type(self).read_from_port, args=(self,))
        listen_process.daemon = True
        listen_process.start()

        while True:
            for packet in self.read_from_queue():
                PacketHandler().handle_packet(packet)

    def read_from_port(self) -> None:
        """Continuosly reads packets from specified host and port and
        puts them in the internal queue.
        """
        retry_delay = self._init_retry_delay
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            sock.settimeout(60)
            try:
                sock.connect(self.host_and_port)
            except ConnectionRefusedError:
                logger.error(
                    f"Server {self.address} refused {self.protocol} connection. Retrying..."
                )

                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, self._max_retry_delay)
                continue

            if self._connect_string:
                sock.send(self._connect_string.encode())

            retry_delay = self._init_retry_delay

            while True:
                try:
                    data = sock.recv(self._max_packet_size)
                    packet = Packet(data, self.protocol, self._host, self._port, time.time())
                    self._queue.put_nowait(packet)
                except (ConnectionResetError, socket.timeout):
                    logger.info(f"Server {self.address} {self.protocol} connection closed.")
                    break

            sock.close()

    def read_from_queue(self, n: int = 1000) -> Generator:
        """Reads n packets from the queue."""
        remaining_packets = n
        while remaining_packets:
            try:
                packet = self._queue.get_nowait()
                if packet.size > 0:
                    yield packet
                    remaining_packets -= 1
            except multiprocessing.queues.Empty:
                remaining_packets = 0
