"""Module that encapsulates requests handlers."""
import logging
import threading
import socketserver

from .packet import Packet
from socket_listener.sinks.base import SinkError

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
            source_name=self.server.provider_name,
            delimiter=self.server.delimiter
        )

        logger.debug(
            "Received {} message(s) from '{}' in {}."
            .format(packet.size, packet.source_name, threading.current_thread().name))

        # TODO: Add a parameter to enable packet logging.
        #       We don't always want to do this.
        # if logging.getLogger().level == logging.DEBUG:
        #    packet.debug()

        try:
            for sink in self.server.sinks:
                sink.publish(packet)
        except SinkError as e:
            self.server.exceptions[type(e)] = e


class UDPRequestHandler(socketserver.BaseRequestHandler, DataPublisherMixIn):
    protocol = "UDP"

    def handle(self):
        """Overrides parent class. In UDP requests,
            self.request consists of a pair of data and client socket."""

        data, _ = self.request
        self.publish(data)
