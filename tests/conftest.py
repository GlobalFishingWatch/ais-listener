"""Reusable objects for tests."""
import socketserver


class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data, socket = self.request
        host, port = self.client_address
        socket.sendto(data.upper(), self.client_address)


class TCPHandler(socketserver.BaseRequestHandler):
    DATA = b"This is a TCP packet."

    def handle(self):
        self.request.sendall(self.DATA)


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


def socket_factory_connect_error(*args, **kwargs):
    return SocketMock(connect_exception=ConnectionError)


def socket_factory_recv_error(*args, **kwargs):
    return SocketMock(recv_exception=ConnectionResetError)
