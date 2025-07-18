import pytest
from unittest import mock

from google.cloud import pubsub_v1

from socket_listener.sinks import GooglePubSub
from socket_listener.packet import Packet


@pytest.mark.parametrize(
    "data_format, raw_data, expected_calls",
    [
        pytest.param(
            "raw",
            b"raw-data",
            [(b"raw-data",)],
            id="publish_raw",
        ),
        pytest.param(
            "split",
            b"msg1\nmsg2",
            [(b"msg1",), (b"msg2",)],
            id="publish_split",
        ),
        pytest.param(
            "split",
            b"this is not really parseable",
            [(b"this is not really parseable",)],
            id="publish_split_fallback_raw",
        ),
    ],
)
def test_publish(monkeypatch, data_format, raw_data, expected_calls):
    mock_publish = mock.Mock()
    mock_client = mock.Mock()
    mock_client.publish = mock_publish
    monkeypatch.setattr(pubsub_v1, "PublisherClient", lambda: mock_client)

    pubsub = GooglePubSub("project-test", "topic-test", data_format=data_format)
    # Ensure raw_data is bytes for Packet
    if isinstance(raw_data, str):
        raw_data = raw_data.encode("utf-8")

    packet = Packet(raw_data)
    packet.metadata = {}

    pubsub.publish(packet)

    # Assert publish called expected number of times with expected args
    assert mock_publish.call_count == len(expected_calls)
    for call_args in expected_calls:
        expected_kwargs = {"topic": pubsub.path, "data": call_args[0], **packet.metadata}
        mock_publish.assert_any_call(**expected_kwargs)


def test_invalid_data_format_raises():
    with pytest.raises(ValueError):
        GooglePubSub("project-test", "topic-test", data_format="invalid-format")
