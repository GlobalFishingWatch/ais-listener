import time
import socket
import threading
import socketserver

import pytest

from ais_listener import transmitters


UDP_DATA = b"This is an UDP packet."
TCP_DATA = b"This is a TCP packet."

NMEA_FILEPATH = "sample/nmea.txt"


class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data, socket = self.request
        host, port = self.client_address
        socket.sendto(data.upper(), self.client_address)


@pytest.mark.parametrize("protocol", ["UDP"])
def test_UDP_client_transmitter(protocol):
    host = "0.0.0.0"
    port = 10111

    # Client transmitter.
    transmitter = transmitters.create(
        protocol=protocol,
        host=host,
        port=port,
    )

    # Server that accepts connections:
    server = socketserver.UDPServer((host, port), UDPHandler, bind_and_activate=False)
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

        # Start transmitter thread.
        transmitter_thread = threading.Thread(
            # name='%s serving' % svrcls,
            target=transmitter.start,
            args=[NMEA_FILEPATH]
        )
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


@pytest.mark.parametrize("protocol", ["TCP"])
def test_TCP_server_transmitter(protocol):
    host = "0.0.0.0"
    port = 10110

    transmitter = transmitters.create(protocol=protocol, host=host, port=port)
    transmitter_thread = threading.Thread(
        # name='%s serving' % svrcls,
        target=transmitter.start,
        args=[NMEA_FILEPATH],
    )
    transmitter_thread.daemon = True
    transmitter_thread.start()

    # Client that receives some data
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.settimeout(60)
    sock.connect((host, port))
    sock.recv(16)
    sock.close()

    transmitter.shutdown()

    # TODO: perform some checks after run.


def test_run_not_implemented_error():
    transmitters.run(
        protocol="invalid", filepath="mock"
    )
