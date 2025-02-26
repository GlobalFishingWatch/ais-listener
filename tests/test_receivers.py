import time
import socket
import threading
import socketserver

import pytest

from ais_listener import receivers


UDP_DATA = b"This is an UDP packet."
TCP_DATA = b"This is a TCP packet."


class SocketMock:
    def __init__(self, connect_exception: Exception = None, recv_exception: Exception = None):
        self._connect_exception = connect_exception
        self._recv_exception = recv_exception

    def connect(self, *args, **kwargs):
        if self._connect_exception is not None:
            raise self._connect_exception

    def setsockopt(self, *args, **kwargs):
        pass

    def settimeout(self, *args, **kwargs):
        pass

    def send(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass

    def recv(self, *args, **kwargs):
        if self._recv_exception is not None:
            raise self._recv_exception

        return b"Mocked data"


@pytest.mark.parametrize("protocol", ["UDP"])
def test_server_receiver(protocol):
    host = "0.0.0.0"
    port = 10110

    receiver = receivers.create(protocol=protocol, host=host, port=port)

    receiver_thread = threading.Thread(
        # name='%s serving' % svrcls,
        target=receiver.start,
        # Short poll interval to make the test finish quickly.
        # Time between requests is short enough that we won't wake
        # up spuriously too many times.
        kwargs={'poll_interval': 0.01}
    )
    receiver_thread.daemon = True
    receiver_thread.start()

    # Client that sends some data:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((host, port))
    sock.send(UDP_DATA)
    sock.close()

    time.sleep(0.1)

    receiver.shutdown()

    # TODO: perform some checks after run.


class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.sendall(TCP_DATA)


@pytest.mark.parametrize("protocol", ["TCP_client"])
def test_client_receiver(protocol):
    host = "0.0.0.0"
    port = 10111

    # Client receiver.
    receiver = receivers.create(
        protocol=protocol,
        host=host,
        port=port,
        connect_string="aFXdRt"
    )

    # Server that accepts connections:
    server = socketserver.TCPServer((host, port), TCPHandler, bind_and_activate=False)
    server.allow_reuse_addres = True
    server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.server_bind()
    server.server_activate()

    with server:
        # Start server thread.
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
        receiver_thread = threading.Thread(
            # name='%s serving' % svrcls,
            target=receiver.start,
        )
        receiver_thread.daemon = True
        receiver_thread.start()

        # Give some time for the server-client interaction.
        time.sleep(0.5)

        # shutdown receiver
        receiver.shutdown()

        # shutdown server.
        server.shutdown()
        receiver_thread.join()
        server.server_close()

        # TODO: perform some checks after run.


def socket_factory_connect_error(*args, **kwargs):
    return SocketMock(
        connect_exception=ConnectionError,
    )


def socket_factory_recv_error(*args, **kwargs):
    return SocketMock(
        recv_exception=ConnectionError,
    )


@pytest.mark.parametrize("protocol", ["TCP_client"])
def test_client_receiver_connection_error(protocol):
    host = "0.0.0.0"
    port = 10111

    receiver = receivers.create(
        protocol=protocol,
        host=host,
        port=port,
        init_retry_delay=0.01,
        socket_factory=socket_factory_connect_error,
    )

    # Start receiver thread.
    receiver_thread = threading.Thread(
        # name='%s serving' % svrcls,
        target=receiver.start,
    )
    receiver_thread.daemon = True
    receiver_thread.start()
    # Give some time for the client to fail and retry.
    time.sleep(0.15)
    receiver.shutdown()
    receiver_thread.join()


@pytest.mark.parametrize("protocol", ["TCP_client"])
def test_client_receiver_recv_error(protocol):
    host = "0.0.0.0"
    port = 10111

    receiver = receivers.create(
        protocol=protocol,
        host=host,
        port=port,
        init_retry_delay=0.01,
        socket_factory=socket_factory_recv_error,
    )

    # Start receiver thread.
    receiver_thread = threading.Thread(
        # name='%s serving' % svrcls,
        target=receiver.start,
    )
    receiver_thread.daemon = True
    receiver_thread.start()
    # Give some time for the client to fail.
    time.sleep(0.15)
    receiver.shutdown()
    receiver_thread.join()
