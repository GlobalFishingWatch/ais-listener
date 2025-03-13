"""Module with class to represent an incoming socket packet."""
import logging
from typing import Generator

from datetime import datetime, timezone
from functools import cached_property
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Packet:
    """Represents an incoming socket packet.

    Attributes:
        time: datetime of the packet reception.

    Args:
        data: Data contained in the packet.
        protocol: Network protocol used.
        source_host: IP of the source.
        source_name: Name of the source.
        delimiter: Delimiter to use when splitting packet data into messages.
    """
    data: bytes
    protocol: str = None
    source_host: tuple = None
    source_name: str = "Unknown"
    delimiter: str = "\n"

    def __post_init__(self) -> None:
        self.time = datetime.now(tz=timezone.utc)

    @cached_property
    def empty(self) -> bool:
        """Returns whether or not the packet is empty."""
        return not self.data

    @cached_property
    def messages_list(self) -> list:
        """Returns list of messages contained in the packet."""
        return list(self.messages)

    @cached_property
    def metadata(self) -> dict:
        """Returns a dictionary with packet metadata."""
        return dict(
            protocol=self.protocol,
            source_host=self.source_host,
            source_name=self.source_name,
            time=self.time.isoformat(),
        )

    @cached_property
    def size(self) -> int:
        """Returns amount of messages contained in the packet."""
        return sum(1 for x in self.messages)

    @property
    def messages(self) -> Generator:
        """Returns generator of messages contained in the packet."""
        return (
            line.strip()
            for line in self.data.decode("utf-8").strip().split(self.delimiter)
            if line
        )
