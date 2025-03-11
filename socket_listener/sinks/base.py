"""Defines Sink base class for Packet publication."""
from socket_listener.packet import Packet


class Sink:
    """Base class for packet sinks."""
    def publish(self, packet: Packet) -> None:
        """Publish instance of Packet to desired destination."""
