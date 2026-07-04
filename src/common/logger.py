import logging
import sys


def password_logger(name: str) -> logging.Logger:
    """Returns a pre-configured logger instance that logs to stdout.

    Args:
        name (str): name of module.

    Returns:
        logging.Logger: logger object.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
