"""Module that encapsulates request handlers."""
import logging
import socketserver

from .packet import Packet

logger = logging.getLogger(__name__)


class UDPRequestHandler(socketserver.BaseRequestHandler):
    """This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto()."""

    protocol = "UDP"

    def handle(self):
        data, _ = self.request
        host, port = self.client_address
        packet = Packet(data, self.server.source_name, self.protocol, host, port)
        packet.log()
        packet.publish(sinks=self.server.sinks)
