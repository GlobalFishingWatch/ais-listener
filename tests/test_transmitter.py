import time
import socket
import threading
import socketserver

import pytest

from socket_listener import transmitters

from tests.conftest import UDPTestHandler


NMEA_FILEPATH = "sample/nmea.txt"
EMPTY_FILEPATH = "sample/empty.txt"


@pytest.mark.parametrize(
    "protocol, filepath",
    [
        pytest.param("UDP", NMEA_FILEPATH, id="NMEA"),
        pytest.param("UDP", EMPTY_FILEPATH, id="EMPTY"),
    ]
)
def test_client_transmitter(protocol, filepath):
    host = "0.0.0.0"
    port = 10111

    # Client transmitter.
    transmitter = transmitters.create(
        protocol=protocol,
        host=host,
        port=port,
    )

    # Server that accepts connections:
    server = socketserver.UDPServer((host, port), UDPTestHandler, bind_and_activate=False)
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

        # Start client transmitter thread.
        transmitter_thread = threading.Thread(target=transmitter.start, args=[filepath])
        transmitter_thread.daemon = True
        transmitter_thread.start()

        # Give some time for the server-client interaction.
        time.sleep(0.1)

        # shutdown transmitter
        transmitter.shutdown()

        # shutdown server.
        server.shutdown()
        transmitter_thread.join()
        server.server_close()

        # TODO: perform some checks after run.


def test_run():
    transmitter, thread = transmitters.run(daemon_thread=True, filepath=EMPTY_FILEPATH)
    transmitter.shutdown()
    thread.join()


def test_run_not_implemented_error():
    transmitters.run(
        protocol="invalid",
        filepath="asd"
    )
