from dataclasses import dataclass
from functools import cached_property


@dataclass
class Packet:
    """Represents a socket packet."""

    data: bytes
    protocol: str
    host: str
    port: int
    timestamp: float

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
