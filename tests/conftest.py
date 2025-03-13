"""Reusable objects for tests."""
import logging
import socketserver


class UDPTestHandler(socketserver.BaseRequestHandler):
    """Test UDP handler that sends received data uppercased."""
    def handle(self):
        data, socket = self.request
        host, port = self.client_address
        socket.sendto(data.upper(), self.client_address)


disable_loggers = ['socket_listener.thread_monitor']


def pytest_configure():
    for logger_name in disable_loggers:
        logger = logging.getLogger(logger_name)
        logger.disabled = True
