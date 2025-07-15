import pytest

from socket_listener import cli


def _run_cli_in_thread(*args):
    (obj, thread), config = cli.cli(
        list(args) + ["--daemon-thread"]
    )
    obj.shutdown()
    thread.join()


def test_cli():
    _run_cli_in_thread(
        "receiver",
        "--protocol", "UDP",
        "--thread-monitor-delay", "0.01",
    )


def test_cli_with_config():
    _run_cli_in_thread(
        "receiver",
        "-c",
        "config/UDP-in-thread.yaml",
        "--provider-name", "marinetraffic",
        "--thread-monitor-delay", "0.01",
    )


def test_cli_no_arguments():
    with pytest.raises(SystemExit):
        cli.cli([])
