import time
import socket
import threading
from unittest import mock

import pytest

from socket_listener import receivers
from socket_listener.sinks import GooglePubSub


@pytest.mark.parametrize("protocol", ["UDP"])
def test_server_receiver(protocol):
    host = "0.0.0.0"
    port = 10110

    receiver = receivers.create(protocol=protocol, host=host, port=port, poll_interval=0.01)
    receiver_thread = threading.Thread(target=receiver.start)
    receiver_thread.daemon = True
    receiver_thread.start()

    # Client that sends some data:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((host, port))
    sock.send(b"This is an UDP packet.")
    sock.close()

    time.sleep(0.1)

    receiver.shutdown()
    receiver_thread.join()

    # TODO: perform some checks after run.


def test_run(monkeypatch):
    sink_mock = mock.Mock(spec=GooglePubSub)
    sink_mock.name = "google_pubsub"

    monkeypatch.setattr(receivers, "create_sink", lambda *x, **y: sink_mock)
    rec, thread = receivers.run(daemon_thread=True, enable_pubsub=True)
    rec.shutdown()
    thread.join()


def test_run_not_implemented_error():
    receivers.run(
        protocol="invalid",
    )
