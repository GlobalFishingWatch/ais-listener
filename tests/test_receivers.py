import time
import socket
import threading
import socketserver

import pytest

from socket_listener import receivers

from tests.conftest import TCPHandler, socket_factory_recv_error, socket_factory_connect_error


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

    # TODO: perform some checks after run.


def run_client_receiver(
    *args,
    socket_factory=socket.socket, host="0.0.0.0", port=10110, sleep=0.3,
    **kwargs
):

    receiver = receivers.create(
        *args,
        host=host,
        port=port,
        init_retry_delay=0.01,
        max_retries=1,
        socket_factory=socket_factory,
        **kwargs,
    )

    # Server that accepts connections:
    server = socketserver.TCPServer((host, port), TCPHandler, bind_and_activate=False)
    server.allow_reuse_addres = True
    server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.server_bind()
    server.server_activate()

    with server:
        server_thread = threading.Thread(
            # name='%s serving' % svrcls,
            target=server.serve_forever,
            # Short poll interval to make the test finish quickly.
            # Time between requests is short enough that we won't wake
            # up spuriously too many times.
            kwargs={'poll_interval': 0.01}
        )
        server_thread.daemon = True
        server_thread.start()

        # Start receiver thread.
        receiver_thread = threading.Thread(target=receiver.start)
        receiver_thread.daemon = True
        receiver_thread.start()

        # Give some time for the server-client interaction.
        time.sleep(sleep)

        # shutdown receiver
        receiver.shutdown()

        # shutdown server.
        server.shutdown()
        receiver_thread.join()
        server.server_close()

        # TODO: perform some checks after run.


@pytest.mark.parametrize("protocol", ["TCP_client"])
def test_client_receiver(protocol):
    run_client_receiver(protocol, socket_factory=socket.socket, connect_string="aFXdRt")


@pytest.mark.parametrize("protocol", ["TCP_client"])
def test_client_receiver_max_retries_exceeded(protocol):
    run_client_receiver(protocol, socket_factory=socket_factory_connect_error)


@pytest.mark.parametrize("protocol", ["TCP_client"])
def test_client_receiver_recv_error(protocol):
    run_client_receiver(protocol, socket_factory=socket_factory_recv_error, sleep=0.4)


def test_run_not_implemented_error():
    receivers.run(
        protocol="invalid",
    )
