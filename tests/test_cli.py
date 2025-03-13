import pytest

from socket_listener import cli


def _run_cli_in_thread(*args):
    obj, thread = cli.cli(
        list(args) + ["--daemon-thread"]
    )
    obj.shutdown()
    thread.join()


def test_cli():
    _run_cli_in_thread(
        "receiver",
        "--protocol", "UDP",
    )


def test_cli_with_config():
    _run_cli_in_thread(
        "receiver",
        "-c",
        "config/UDP-ais-in-thread.yaml",
    )


def test_cli_no_arguments():
    with pytest.raises(SystemExit):
        cli.cli([])
