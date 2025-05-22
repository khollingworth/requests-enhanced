"""
Logging configuration for requests-enhanced.
"""

import logging
from typing import Optional

# Default format for log messages
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class RequestsEnhancedFormatter(logging.Formatter):
    """Custom formatter for requests-enhanced logs."""

    def __init__(self, fmt: Optional[str] = None):
        """
        Initialize the formatter with the given format string.

        Args:
            fmt: Log format string. If None, DEFAULT_LOG_FORMAT will be used.
        """
        if fmt is None:
            fmt = DEFAULT_LOG_FORMAT
        super().__init__(fmt=fmt)


def configure_logger(
    logger: logging.Logger,
    level: int = logging.INFO,
    handler: Optional[logging.Handler] = None,
    log_format: Optional[str] = None,
) -> logging.Logger:
    """
    Configure a logger with the specified level, handler, and format.

    Args:
        logger: The logger to configure
        level: Logging level (e.g., logging.INFO, logging.DEBUG)
        handler: Optional handler to add to the logger. If None, a StreamHandler will be
            created.
        log_format: Format string for log messages. If None and handler has no
                   formatter, DEFAULT_LOG_FORMAT will be used.

    Returns:
        The configured logger
    """
    # Set logger level
    logger.setLevel(level)

    # Create handler if not provided
    if handler is None:
        handler = logging.StreamHandler()
        handler.setLevel(level)

    # Handle formatter based on provided log_format and existing formatter
    if log_format is not None:
        # If explicit log_format is provided, use it regardless of existing formatter
        formatter = RequestsEnhancedFormatter(log_format)
        handler.setFormatter(formatter)
    elif not handler.formatter:
        # If no formatter exists on handler and no log_format provided, use default
        formatter = RequestsEnhancedFormatter()
        handler.setFormatter(formatter)
    # If handler already has a formatter and no log_format is specified, keep it

    # Add handler to logger if not already added
    if handler not in logger.handlers:
        logger.addHandler(handler)

    return logger
