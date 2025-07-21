"""Contains class for Google Pub/Sub publication."""
import logging
from typing import Callable
from functools import cached_property

from google.cloud import pubsub_v1
from google.api_core import exceptions

from socket_listener.sinks.base import Sink, SinkError
from socket_listener.packet import Packet

logger = logging.getLogger(__name__)


class Format:
    RAW = "raw"
    SPLIT = "split"

    ALL = frozenset([RAW, SPLIT])


class GooglePubSubError(SinkError):
    pass


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
    def publish_methods(self) -> dict[str, Callable[[Packet], None]]:
        return {
            Format.RAW: self._publish_raw,
            Format.SPLIT: self._publish_split,
        }

    def publish(self, packet: Packet) -> None:
        """Publish a Packet to Google Pub/Sub using the selected format."""
        self.publish_methods[self._data_format](packet)

    def _publish_raw(self, packet: Packet) -> None:
        self._publish(data=packet.data, **packet.metadata)

    def _publish_split(self, packet: Packet) -> None:
        # Attempt to split the packet. If it cannot be split, it will contain a single raw message.
        for message in packet.messages:
            self._publish(data=message, **packet.metadata)

    def _publish(self, data: bytes, **attrs: str) -> None:
        try:
            future = self._publisher.publish(topic=self.path, data=data, **attrs)
            message_id = future.result(timeout=5.0)
            logger.debug(f"Published message ID: {message_id}")
        except exceptions.PermissionDenied as e:
            # This is a critical error — the server must be terminated in this case.
            logger.critical(f"Failed to publish message: {e}")
            raise GooglePubSubError(e)
        except Exception as e:
            # The cause of this error is unknown; we simply log it
            logger.critical(f"Failed to publish message: {e}")

    def _validate_data_format(self, data_format: str) -> str:
        if data_format not in Format.ALL:
            raise ValueError(
                f"Invalid data_format: {data_format}. Must be one of: {Format.ALL}"
            )

        return data_format
