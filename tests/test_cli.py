import logging

import pytest

from socket_listener import cli


@pytest.fixture(autouse=True)
def cleanup_logging_handlers():
    """Cleanup multiprocessing logging handlers."""
    try:
        yield
    finally:
        mp_logger = logging.root.manager.loggerDict.get("multiprocessing")
        if mp_logger:
            for handler in mp_logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    mp_logger.addHandler(logging.NullHandler())
                    mp_logger.removeHandler(handler)


def test_cli(tmp_path, cleanup_logging_handlers):
    args = [
        "receiver",
        "-v",
        "--protocol", "TCP_client",
        "--max-retries", "1",
        "--init-retry-delay", "0"
    ]

    cli.cli(args)

    with pytest.raises(SystemExit):
        cli.cli([])


def test_cli_no_rich_logging(tmp_path, cleanup_logging_handlers):
    args = [
        "receiver",
        "--no-rich-logging",
        "--protocol", "TCP_client",
        "--max-retries", "1",
        "--init-retry-delay", "0"
    ]

    cli.cli(args)
