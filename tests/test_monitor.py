import time

from socket_listener.monitor import ThreadMonitor


def test_run():
    monitor = ThreadMonitor(delay=0)
    monitor.start()
    time.sleep(0.1)
    monitor.stop()
