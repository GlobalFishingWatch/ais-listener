"""Contains class for Google Pub/Sub publication."""
import logging
from google.cloud import pubsub_v1

from functools import cached_property

from socket_listener.sinks.base import Sink
from socket_listener.packet import Packet

logger = logging.getLogger(__name__)


class Format:
    RAW = "raw"
    SPLIT = "split"

    ALL = {RAW, SPLIT}


class GooglePubSub(Sink):
    """Publish Packet instances to Google PubSub service.

    Args:
        project_id:
            Google project id.

        topic_id:
            Google PubSub topic.

        data_format:
            Either 'raw' or 'split'. Defaults to 'raw'.
    """
    name = "google_pubsub"

    def __init__(self, project_id: str, topic_id: str, data_format: str = Format.RAW) -> None:
        self._project_id = project_id
        self._topic_id = topic_id
        self._data_format = self._validate_data_format(data_format)

        self._publisher = pubsub_v1.PublisherClient()

    @cached_property
    def path(self):
        return self._publisher.topic_path(self._project_id, self._topic_id)

    @cached_property
    def publish_methods(self):
        return {
            Format.RAW: self._publish_raw,
            Format.SPLIT: self._publish_split,
        }

    def publish(self, packet: Packet) -> None:
        print("JAJAJAJJA", packet)
        self.publish_methods[self._data_format](packet)

    def _publish_raw(self, packet: Packet) -> None:
        self._publisher.publish(self.path, packet.data, **packet.metadata)

    def _publish_split(self, packet: Packet) -> None:
        # If packet.messages fails to split the packet, will return just the raw data.
        for message in packet.messages:
            self._publisher.publish(self.path, message, **packet.metadata)

    def _validate_data_format(self, data_format: str) -> str:
        if data_format not in Format.ALL:
            raise ValueError(
                f"Invalid data_format: {data_format}. Must be one of: {Format.ALL}"
            )

        return data_format
