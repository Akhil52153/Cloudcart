"""Logging configuration with Rich formatting."""

import logging
from rich.logging import RichHandler


def setup_logger(name: str = "cloudcart") -> logging.Logger:
    """
    Set up a logger with Rich formatting.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Rich handler for pretty console output
        handler = RichHandler()
        formatter = logging.Formatter(
            "%(message)s",
            datefmt="[%X]"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger