"""A class to represent a socket packet."""
import logging
import threading

from datetime import datetime, timezone
from dataclasses import dataclass
from functools import cached_property

logger = logging.getLogger(__name__)


@dataclass
class Packet:
    """Represents a received socket packet."""

    data: bytes
    source: str = "Unknown"
    protocol: str = None
    host: str = None
    port: int = None

    def __post_init__(self):
        self.time = datetime.now(tz=timezone.utc)

    @cached_property
    def address(self) -> str:
        """Unified string version of the host and port properties."""
        return f"{self.host}:{self.port}"

    @cached_property
    def decoded_data(self):
        """Returns decoded and stripped data."""
        return self.data.decode("utf-8").strip()

    @cached_property
    def messages(self, delimiter: str = "\n"):
        """Returns messages contained in the packet
        delimited by the provided delimiter, as a list of strings."""

        return list(line.strip() for line in self.decoded_data.split(delimiter) if line)

    @cached_property
    def size(self):
        """Returns the amount of messages contained in the packet."""
        return len(self.messages)

    @cached_property
    def empty(self):
        """Returns whether or not the packet is empty."""
        return not self.data

    def log(self):
        """Logs amount of received messages at INFO level and each message at DEBUG level."""
        if self.size > 0:
            logger.info(
                "Received {} messages from {} in {}."
                .format(self.size, self.host, threading.current_thread().name))

        for message in self.messages:
            logger.debug(message)

    def publish(self, sinks: list) -> None:
        """Publish received packets to provided sinks."""
        for sink in sinks:
            sink.publish(self)
