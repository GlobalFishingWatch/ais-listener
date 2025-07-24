# health_server.py
import logging
import threading
import http.server
import socketserver

from typing import Any, Optional, Type
from functools import cached_property

logger = logging.getLogger(__name__)


class CustomHTTPServer(socketserver.ThreadingTCPServer):
    """A custom ThreadingTCPServer that allows passing an instance of
    HealthCheckServer to its request handlers."""
    health_server: Optional['HealthCheckServer']

    def __init__(
        self, *args: Any,
        health_server: Optional['HealthCheckServer'] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.health_server = health_server


class HealthCheckHandler(http.server.BaseHTTPRequestHandler):
    """HTTP Request Handler for Kubernetes health and readiness probes.
    It accesses the state from the `HealthCheckServer` instance."""
    health_server: 'HealthCheckServer'

    # Use *args to capture (request, client_address, server)
    def __init__(self, *args: Any, server: CustomHTTPServer, **kwargs: Any) -> None:
        self.health_server = server.health_server
        super().__init__(*args, server=server, **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        """Suppresses logging of every health check request for cleaner logs."""
        pass

    def do_GET(self) -> None:
        """Handles GET requests for /healthz and /readyz."""
        if self.path == '/healthz':
            self._handle_healthz()
        elif self.path == '/readyz':
            self._handle_readyz()
        else:
            self._handle_not_found()

    def _handle_healthz(self) -> None:
        """Handles requests to the /healthz endpoint."""
        if self.health_server.get_healthy_status():
            self._send_http_response(200, "OK")
        else:
            self._send_http_response(500, "NOT HEALTHY")

    def _handle_readyz(self) -> None:
        """Handles requests to the /readyz endpoint."""
        if self.health_server.get_ready_status():
            self._send_http_response(200, "READY")
        else:
            self._send_http_response(503, "NOT READY")

    def _handle_not_found(self) -> None:
        """Handles requests for unknown paths."""
        self._send_http_response(404, "Not Found")

    def _send_http_response(self, code: int, message: str) -> None:
        self.send_response(code)
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))


class HealthCheckServer(threading.Thread):
    """Thread that runs a simple HTTP server for Kubernetes health and readiness probes."""

    _host: str
    _port: int
    _handler: Type[HealthCheckHandler]

    def __init__(self, host: str = "0.0.0.0", port: int = 8080) -> None:
        super().__init__()
        self.daemon = True
        self._host = host
        self._port = port
        self._handler = HealthCheckHandler

        self._ready_lock = threading.Lock()
        self._is_ready = False

        self._healthy_lock = threading.Lock()
        self._is_healthy = True

        self._is_running = threading.Event()

    @cached_property
    def server_address(self) -> str:
        """Unified string version of the host and port properties."""
        return f"{self._host}:{self._port}"

    @cached_property
    def http_server(self) -> CustomHTTPServer:
        """
        Lazily creates and returns the CustomHTTPServer instance.
        """
        logger.debug(f"Creating CustomHTTPServer instance for {self.server_address}...")
        return CustomHTTPServer((self._host, self._port), self._handler, health_server=self)

    def set_ready_status(self, status: bool) -> None:
        """Sets the application's readiness status (thread-safe)."""
        with self._ready_lock:
            self._is_ready = status
        logger.info(f"HealthCheckServer: Readiness status set to: {self._is_ready}")

    def set_healthy_status(self, status: bool) -> None:
        """Sets the application's health status (thread-safe)."""
        with self._healthy_lock:
            self._is_healthy = status
        logger.info(f"HealthCheckServer: Health status set to: {self._is_healthy}")

    def get_ready_status(self) -> bool:
        """Gets the application's readiness status (thread-safe)."""
        with self._ready_lock:
            return self._is_ready

    def get_healthy_status(self) -> bool:
        """Gets the application's health status (thread-safe)."""
        with self._healthy_lock:
            return self._is_healthy

    def run(self) -> None:
        """Overrides parent class (threading.Thread) implementation to run the HTTP server."""
        logger.info(f"Health check server starting on {self.server_address}...")
        try:
            self._is_running.set()
            self.http_server.serve_forever()
        except Exception as e:
            logger.error(f"Health check server encountered an error: {e}", exc_info=True)
            self.set_healthy_status(False)
            self.set_ready_status(False)
        finally:
            logger.info("Health check server stopped.")
            self._is_running.clear()
            self.http_server.server_close()

    def stop(self) -> None:
        """Gracefully shuts down the HTTP server."""
        logger.info("HealthCheckServer: Signaling HTTP server to shut down...")
        try:
            self.http_server.shutdown()
        except Exception as e:
            logger.warning(f"Error during HTTP server shutdown: {e}")

        self.join(timeout=5)
        if self.is_alive():
            logger.warning("HealthCheckServer thread did not terminate gracefully.")
