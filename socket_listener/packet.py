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
        time:
            datetime of the packet reception.

    Args:
        data:
            Raw data contained in the packet.

        protocol:
            Network protocol used.

        source_host:
            IP of the source.

        source_name:
            Name of the source.

        delimiter:
            Delimiter to use when splitting packet data into messages.

        decode_method:
            The method to use when trying to decode the packet data.
    """
    data: bytes
    protocol: str = None
    source_host: tuple = None
    source_name: str = "Unknown"
    delimiter: str = "\n"
    decode_method: str = "utf-8"

    def __post_init__(self) -> None:
        self.time = datetime.now(tz=timezone.utc)

    @cached_property
    def decoded_data(self) -> bool:
        """Returns the decoded data."""
        return self.data.decode(self.decode_method)

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
        return sum(1 for _ in self.messages)

    @property
    def messages(self) -> Generator[bytes, None, None]:
        """Returns generator of messages contained in the packet.

        Tries to decode and split the message into individual parts.
        If that fails, yields the raw message as bytes.
        """
        try:
            for line in self.decoded_data.strip().split(self.delimiter):
                if line:
                    yield line.strip().encode(self.decode_method)
        except Exception as e:
            logger.debug("Failed trying to decode or split the packet into messages.")
            logger.debug(f"Exception: {e}.")
            logger.debug("Will return a single message with raw data.")
            yield self.data

    def debug(self):
        """Logs the packet.

        If can be decoded and splitted, logs each element individually.
        Otherwise, logs the raw packet.
        """
        for m in self.messages:
            logger.debug(m)
