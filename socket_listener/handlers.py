"""Module that encapsulates requests handlers."""
import logging
import threading
import socketserver

from .packet import Packet

logger = logging.getLogger(__name__)


class DataPublisherMixin:
    """Data publisher mixin to use in handlers."""

    def publish(self, data: bytes, host: str):
        """Publishes data to configured sinks.

        Args:
            data: Data to be published.
            host: IP of incoming request.
        """
        packet = Packet(
            data,
            protocol=self.protocol,
            source_host=host,
            source_name=self.server.source_name,
            delimiter=self.server.delimiter
        )

        for sink in self.server.sinks:
            sink.publish(packet)

        logger.debug(
            "Published {} messages to {} received from {} in {}."
            .format(packet.size, sink.path, host, threading.current_thread().name))


class UDPRequestHandler(socketserver.BaseRequestHandler, DataPublisherMixin):
    protocol = "UDP"

    def handle(self):
        """Overrides parent class. In UDP requests,
            self.request consists of a pair of data and client socket."""

        data, _ = self.request
        host, _ = self.client_address

        self.publish(data, host)
