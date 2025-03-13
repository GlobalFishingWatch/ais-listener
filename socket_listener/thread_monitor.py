import time
import logging
import threading

logger = logging.getLogger(__name__)


class ThreadMonitor(threading.Thread):
    """Thread that periodically logs the number of active threads.

    Start it with .start() method from parent class.

    Args:
        delay: Number of seconds between each log entry.
    """
    def __init__(self, delay: int = 5):
        super().__init__()
        self._delay = delay
        self._is_done = False

    def stop(self):
        self._is_done = True

    def run(self):
        """Overrides parent class implementation."""
        while not self._is_done:
            time.sleep(self._delay)
            logger.info(f"Number of active threads: {threading.active_count()}")
