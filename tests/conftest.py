"""Reusable objects for tests."""
import socketserver


class UDPTestHandler(socketserver.BaseRequestHandler):
    """Test UDP handler that sends received data uppercased."""
    def handle(self):
        data, socket = self.request
        host, port = self.client_address
        socket.sendto(data.upper(), self.client_address)
