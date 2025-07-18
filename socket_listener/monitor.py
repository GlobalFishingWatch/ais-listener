"""Module with monitoring utilities."""
import time
import logging
import threading
from typing import Any, Callable, Dict, Type
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class Monitor(ABC, threading.Thread):
    """Thread that periodically executes some operation.

    Start it with .start() method from parent class.

    Args:
        delay:
            Number of seconds between each operation execution.
    """
    def __init__(self, delay: int = 5):
        super().__init__()
        self._delay = delay
        self._is_done = False

    def stop(self):
        self._is_done = True

    def run(self):
        """Overrides parent class (threading.Thread) implementation."""
        while not self._is_done:
            time.sleep(self._delay)
            self.operation()

    @abstractmethod
    def operation(self):
        """The operation to execute in this Monitor instance."""


class ThreadMonitor(Monitor):
    """Thread that periodically logs the number of active threads."""
    def operation(self):
        logger.info(f"Number of active threads: {threading.active_count()}")


class ExceptionMonitor(Monitor):
    """Thread that periodically checks saved exceptions and stops the server when found.

    Args:
        exceptions:
            A mapping with {type(exception): exception} to be checked.

        shutdown_server:
            Function to shutdown the server.

        kwargs:
            Any keyword argument to be passed to Monitor base class.
    """
    def __init__(
        self,
        exceptions: Dict[Type[BaseException], BaseException],
        shutdown_server: Callable[..., None],
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self._exceptions = exceptions
        self._shutdown_server = shutdown_server

    def operation(self):
        if self._exceptions:
            logger.error(f"Exceptions detected: {self._exceptions}.")
            logger.error("Shutting down server...")
            self.stop()
            self._shutdown_server()
