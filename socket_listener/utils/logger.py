"""Logger utitlities."""
import logging

from rich.logging import RichHandler


_TIME_ENTRY = "%(asctime)s - "
_DEFAULT_LOG_FORMAT = f"{_TIME_ENTRY}%(name)s - %(message)s"


def setup_logger(
    verbose: bool = False,
    format_: str = _DEFAULT_LOG_FORMAT,
    warning_level: tuple = (),
    error_level: tuple = (),
    force: bool = False,
    rich: bool = True,
    log_file: str = None,
) -> None:
    """Configures the root logger.

    Args:
        level:
            Logger level.

        format_:
            Logger format.

        warning_level:
            List of packages/modules for which to set the log level as WARNING.

        error_level:
            List of packages/modules for which to set the log level as ERROR.

        force:
            If true, forces the root logger config replacing the one done on other places.

        rich:
            Whether to use rich library to colorize console output.

        log_file:
            Path to file in which to save logs.
    """

    handlers = []

    if rich:
        rich_format = format_.replace(_TIME_ENTRY, "")
        rich_handler = RichHandler()
        rich_handler.setFormatter(logging.Formatter(rich_format))
        handlers.append(rich_handler)
    else:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(format_))
        handlers.append(stream_handler)

    if log_file is not None:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(format_))
        handlers.append(file_handler)

    level = logging.INFO
    if verbose:
        level = logging.DEBUG

    logging.basicConfig(level=level, handlers=handlers, force=force)

    for module in warning_level:
        logging.getLogger(module).setLevel(logging.WARNING)

    for module in error_level:
        logging.getLogger(module).setLevel(logging.ERROR)
