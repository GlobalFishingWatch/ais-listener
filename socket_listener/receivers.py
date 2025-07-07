"""Classes for continuous socket data reception and publication.

This module provides a base class for "receiver" objects and also concrete implementations.
These objects support the continuous data reception from network sockets and publication
to the configured data destinations or sinks.
"""

import logging
import threading
import socketserver
from typing import Any

from importlib import resources
from abc import ABC, abstractmethod
from functools import cached_property

from gfw.common.io import yaml_load

from socket_listener import assets

from .handlers import UDPRequestHandler
from .monitor import ThreadMonitor
from .sinks import create_sink


logger = logging.getLogger(__name__)

DEFAULT_IP_CLIENT_MAPPING_FILE = "ip-client-mapping.yaml"


def run(
    *args,
    pubsub: bool = False,
    pubsub_project: str = None,
    pubsub_topic: str = None,
    pubsub_data_format: str = "raw",
    daemon_thread: bool = False,
    unknown_unparsed_args: list = None,
    unknown_parsed_args: dict = None,
    **kwargs,
):
    """Runs a socket receiver service inside a separate thread.

    Args:
        *args:
            Positional arguments for socket receiver constructor.

        pubsub:
            Enables publication to Google Pub/Sub service.

        pubsub_project:
            GCP project id for Pub/Sub integration.

        pubsub_topic_id:
            Topic id for Pub/Sub integration.

        pubsub_data_format:
            The data format for for Pub/Sub integration.

        daemon_thread:
            If true, makes the thread daemonic.

        **kwargs: Keyword arguments for socket receiver constructor.

    Returns:
        A tuple (receiver, thread).
    """
    sinks_config = {}
    if pubsub:
        sinks_config["google_pubsub"] = dict(
            project_id=pubsub_project,
            topic_id=pubsub_topic,
            data_format=pubsub_data_format,
        )

    try:
        receiver = create(*args, **kwargs, sinks_config=sinks_config)
    except NotImplementedError as e:
        logger.error(e)
        return

    thread = threading.Thread(target=receiver.start)
    thread.daemon = daemon_thread
    thread.start()

    return receiver, thread


def create(protocol="UDP", *args, **kwargs) -> 'SocketReceiver':
    receivers = {
        UDPSocketReceiver.protocol: UDPSocketReceiver,
    }

    if protocol not in receivers:
        raise NotImplementedError(f"Receiver for protocol '{protocol}' not implemented.")

    return receivers[protocol].build(*args, **kwargs)


class SocketReceiver(ABC):
    """Base class for socket data reception.

    A socket receiver object implemented using the socketserver module from the standard library.
    A ThreadMonitor object will be logging the number of threads alive every N number of seconds.

    Args:
        poll_interval:
            Seconds to wait before poll for server shutdown.

        thread_monitor_delay:
            Seconds between each log entry with number of active threads.

        host:
            The IP address to use.

        port:
            The port to use.

        max_packet_size:
            The maximum amount of data to be received at once.

        delimiter:
            Symbol to use as delimiter while splitting packets into messages.

        sinks:
            List of sinks in which to publish incoming packets.

        ip_client_mapping:
            A mapping (IP -> client_name).
    """
    def __init__(
        self,
        poll_interval: float = 0.5,
        thread_monitor_delay: int = 5,
        host: str = "0.0.0.0",
        port: int = 10110,
        max_packet_size: int = 4096,
        delimiter: str = "\n",
        sinks=(),
        ip_client_mapping: dict = None,
    ) -> None:

        self._poll_interval = poll_interval
        self._thread_monitor = ThreadMonitor(delay=thread_monitor_delay)

        self._server = self.create_socketserver((host, port))

        # Following proprerties are needed by the request handler.
        # TODO: encapsulate these properties in ServerConfig class?
        self._server.max_packet_size = max_packet_size
        self._server.delimiter = delimiter
        self._server.sinks = sinks
        self._server.ip_client_mapping = ip_client_mapping or {}

    @staticmethod
    @abstractmethod
    def create_socketserver(server_address: tuple[str, int], **kwargs):
        """Instantiates a socketserver object."""

    @classmethod
    def build(
        cls, sinks_config: dict = None, ip_client_mapping_file: str = None, **kwargs: Any
    ) -> 'SocketReceiver':
        """Builds a socket receiver object.

        Args:
            sinks_config:
                Dictionary with sinks configuration.

            ip_client_mapping_file:
                Path to file with ip->clients mappings.

            **kwargs:
                keyword arguments for SocketReceiver constructor.
        """
        sinks = [create_sink(n, **v) for n, v in (sinks_config or {}).items()]

        if ip_client_mapping_file is None:
            ip_client_mapping_file = str(resources.files(assets) / DEFAULT_IP_CLIENT_MAPPING_FILE)

        logger.info(f"Loading (IP -> clients_name) mapping from {ip_client_mapping_file}.")
        ip_client_mapping = yaml_load(ip_client_mapping_file)

        return cls(sinks=sinks, ip_client_mapping=ip_client_mapping, **kwargs)

    @property
    def server(self):
        return self._server

    @cached_property
    def server_address(self) -> str:
        """Unified string version of the host and port properties."""
        host, port = self._server.server_address
        return f"{host}:{port}"

    @cached_property
    def sinks(self):
        """Returns list of sinks names."""
        return [s.name for s in self._server.sinks]

    def start(self) -> None:
        """Starts the socket receiver."""
        logger.info(f"Listening {self.protocol} socket on {self.server_address}...")
        logger.info(f"{len(self.sinks)} sink(s) configured ({', '.join(self.sinks)}):")
        for sink in self._server.sinks:
            logger.info(f"{sink.name}: {sink.path}")

        self._thread_monitor.start()
        with self._server:
            self._server.serve_forever(poll_interval=self._poll_interval)

    def shutdown(self):
        self._server.shutdown()
        self._thread_monitor.stop()


class UDPSocketReceiver(SocketReceiver):
    """UDP socket receiver."""

    protocol = "UDP"

    @staticmethod
    def create_socketserver(server_address: tuple[str, int], **kwargs):
        return socketserver.ThreadingUDPServer(server_address, UDPRequestHandler, **kwargs)
