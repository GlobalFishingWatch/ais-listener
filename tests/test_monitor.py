import time
from unittest.mock import MagicMock
from google.api_core.exceptions import PermissionDenied

from socket_listener.monitor import ThreadMonitor, ExceptionMonitor

from socket_listener.receivers import UDPSocketReceiver


def test_run():
    monitor = ThreadMonitor(delay=0)
    monitor.start()
    time.sleep(0.1)
    monitor.stop()


def test_exception_monitor_detects_permission_denied_exception():
    # Create UDP receiver with a random port to avoid conflicts
    receiver = UDPSocketReceiver(port=0)

    # Inject a PermissionDenied exception instance into the shared exceptions list
    permission_error = PermissionDenied("Permission denied for publishing")
    receiver.server.exceptions[type(permission_error)] = permission_error

    # Mock shutdown_server function to verify it gets called
    shutdown_mock = MagicMock()

    # Create the ExceptionMonitor with the shared exceptions list and shutdown mock
    monitor = ExceptionMonitor(
        exceptions=receiver.server.exceptions,
        shutdown_server=shutdown_mock,
        delay=1,
    )

    # Call the operation method manually to check detection (would log error)
    monitor.operation()

    # Assert the PermissionDenied exception is present in the shared list
    assert type(permission_error) in receiver.server.exceptions

    # Call stop() which should trigger shutdown_server
    monitor.stop()
    shutdown_mock.assert_called_once()
