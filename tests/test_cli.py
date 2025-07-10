import pytest

from importlib import resources

from socket_listener import cli
from socket_listener import assets


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
    ip_client_mapping_file = resources.files(assets) / "ip-client-mapping.yaml"

    _run_cli_in_thread(
        "receiver",
        "-c",
        "config/UDP-in-thread.yaml",
        "--ip-client-mapping-file",
        f"{ip_client_mapping_file}",
        "--thread-monitor-delay", "0.01",
    )


def test_cli_no_arguments():
    with pytest.raises(SystemExit):
        cli.cli([])
