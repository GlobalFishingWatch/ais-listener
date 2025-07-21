"""Defines Sink base class for Packet publication."""
from socket_listener.packet import Packet
from abc import ABC, abstractmethod


class SinkError(Exception):
    pass


class Sink(ABC):
    """Base class for packet sinks."""
    @abstractmethod
    def publish(self, packet: Packet) -> None:
        """Publish instance of Packet to desired destination."""
