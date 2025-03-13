import time
import socket
import threading

import pytest

from socket_listener import receivers


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


def test_run_not_implemented_error():
    receivers.run(
        protocol="invalid",
    )
