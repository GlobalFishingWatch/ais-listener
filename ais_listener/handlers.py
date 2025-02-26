import time
import logging
import threading
import socketserver

from typing import Generator

from .packet import Packet

logger = logging.getLogger(__name__)


class PacketHandler:
    """Handler for incoming packets."""

    def handle_packet(self, packet: Packet) -> None:
        cur_thread = threading.current_thread()
        if packet.size > 0:
            logger.info(
                "{}: Received {} messages from {} in {}.".format(
                    packet.protocol, packet.size, packet.host, cur_thread.name
                )
            )

        for message in packet.messages:
            logger.debug(message)
            # In here post to sinks...e.g. Pub/Sub


class UDPRequestHandler(socketserver.BaseRequestHandler, PacketHandler):
    """This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto()."""

    protocol = "UDP"

    def handle(self):
        data, socket = self.request
        host, port = self.client_address
        packet = Packet(data, self.protocol, host, port)
        self.handle_packet(packet)


class TCPRequestHandler(socketserver.BaseRequestHandler):
    """The request handler class for our server.
    It is instantiated once per connection to the server."""

    def handle(self) -> None:
        logger.info(f"Received request from {self.client_address}:")
        messages = self._read_messages(self.server.data_path)

        chunk = []
        for m in messages:
            chunk.append(m)
            if len(chunk) >= self.server.max_chunk_size:
                self._send_messages(chunk)
                chunk = []

    def _read_messages(self, path) -> Generator:
        logger.info(f"Reading messages from {path}.")
        with open(path, "r") as f:
            for line in f:
                yield line.strip().encode("utf-8")

    def _send_messages(self, messages: list[bytes]) -> None:
        data = b"\n".join(messages)
        self.request.sendall(b"\n".join(messages))
        logger.info(f"Finished sending {len(messages)} messages to {self.client_address}.")
        logger.debug(f"Data sent: {data}")
        time.sleep(self.server.delay)
