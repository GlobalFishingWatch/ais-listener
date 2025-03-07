from socket_listener.utils import logger


def test_setup_logger_warn_error_levels():
    logger.setup_logger(
        warning_level=["cloudpathlib"],
        error_level=["cloudpathlib"])


def test_setup_logger_no_rich():
    logger.setup_logger(rich=False)


def test_setup_logger_verbose():
    logger.setup_logger(verbose=True)
