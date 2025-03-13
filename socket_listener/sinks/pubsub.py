"""Contains class for Google Pub/Sub publication."""
import logging
from google.cloud import pubsub_v1

from functools import cached_property

from socket_listener.sinks.base import Sink
from socket_listener.packet import Packet

logger = logging.getLogger(__name__)


class GooglePubSub(Sink):
    """Publish Packet instances to Google PubSub service.

    Args:
        project_id: Google project id.
        topic_id: Google PubSub topic.
    """
    name = "google_pubsub"

    def __init__(self, project_id: str, topic_id: str) -> None:
        self._project_id = project_id
        self._topic_id = topic_id

        self._publisher = pubsub_v1.PublisherClient()

    @cached_property
    def path(self):
        return self._publisher.topic_path(self._project_id, self._topic_id)

    def publish(self, packet: Packet) -> None:
        for message in packet.messages:
            future = self._publisher.publish(
                self.path,
                message.encode("utf-8"),
                **packet.metadata
            )

            logger.debug(f"Pub/Sub future result: {future.result()}")
