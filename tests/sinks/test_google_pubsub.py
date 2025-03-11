from unittest import mock

from google.cloud import pubsub_v1

from socket_listener.sinks import GooglePubSub
from socket_listener.packet import Packet


def test_publish(monkeypatch):
    monkeypatch.setattr(pubsub_v1, "PublisherClient", mock.Mock(pubsub_v1.PublisherClient))

    pubsub = GooglePubSub("project-test", "topic-test")
    packet = Packet(b"123")
    pubsub.publish(packet)
