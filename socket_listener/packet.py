import time

from dataclasses import dataclass
from functools import cached_property


@dataclass
class Packet:
    """Represents a received socket packet."""

    data: bytes
    protocol: str = None
    host: str = None
    port: int = None

    def __post_init__(self):
        self.timestamp = time.time()

    @cached_property
    def decoded_data(self):
        return self.data.decode("utf-8").strip()

    @cached_property
    def messages(self, delimiter: str = "\n"):
        """Returns the list of messages contained in the packet
        delimited by the provided delimiter."""

        return list(line.strip() for line in self.decoded_data.split(delimiter) if line)

    @cached_property
    def size(self):
        """Returns the amount of messages contained in the packet."""
        return len(self.messages)

    @cached_property
    def empty(self):
        return not self.data
