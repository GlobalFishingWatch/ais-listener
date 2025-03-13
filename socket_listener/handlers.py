"""Module that encapsulates request handlers."""
import logging
import threading
import socketserver

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
