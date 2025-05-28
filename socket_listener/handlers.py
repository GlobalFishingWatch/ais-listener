"""Module that encapsulates requests handlers."""
import logging
import threading
import socketserver

from .packet import Packet

logger = logging.getLogger(__name__)


class DataPublisherMixIn:
    """Data publisher MixIn to use in handlers."""

    def publish(self, data: bytes):
        """Publishes data to configured sinks.

        Args:
            data: the data to publish.
        """
        host, _ = self.client_address

        packet = Packet(
            data,
            protocol=self.protocol,
            source_host=host,
            source_name=self.server.ip_client_mapping.get(host, "Unknown"),
            delimiter=self.server.delimiter
        )

        logger.debug(
            "Received {} message(s) from {} ({}) in {}."
            .format(packet.size, host, packet.source_name, threading.current_thread().name))

        if logging.getLogger().level == logging.DEBUG:
            for m in packet.messages:
                logger.debug(m)

        for sink in self.server.sinks:
            sink.publish(packet)


class UDPRequestHandler(socketserver.BaseRequestHandler, DataPublisherMixIn):
    protocol = "UDP"

    def handle(self):
        """Overrides parent class. In UDP requests,
            self.request consists of a pair of data and client socket."""

        data, _ = self.request
        self.publish(data)
