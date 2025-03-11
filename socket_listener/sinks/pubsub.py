"""Contains class for Google Pub/Sub publication."""
import logging
from google.cloud import pubsub_v1

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

    def publish(self, packet: Packet) -> None:
        topic_path = self._publisher.topic_path(self._project_id, self._topic_id)

        for message in packet.messages:
            future = self._publisher.publish(
                topic_path,
                message.encode("utf-8"),
                protocol=packet.protocol,
                address=packet.address,
                timestamp=packet.time.isoformat(),
                source=packet.source
            )
            logger.info(future.result())

        logger.info(f"Published packet messages to {topic_path}.")
