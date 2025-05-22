"""
Tests for the logging functionality.
"""

import logging
import io

from requests_enhanced.logging import (
    configure_logger,
    RequestsEnhancedFormatter,
    DEFAULT_LOG_FORMAT,
)


def test_configure_logger_with_defaults():
    """Test configuring a logger with default settings."""
    logger = logging.getLogger("test_default")
    logger.handlers.clear()  # Ensure clean state

    result = configure_logger(logger)

    assert result is logger
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)
    assert isinstance(logger.handlers[0].formatter, RequestsEnhancedFormatter)


def test_configure_logger_with_custom_level():
    """Test configuring a logger with a custom level."""
    logger = logging.getLogger("test_level")
    logger.handlers.clear()

    configure_logger(logger, level=logging.DEBUG)

    assert logger.level == logging.DEBUG
    assert logger.handlers[0].level == logging.DEBUG


def test_configure_logger_with_custom_handler():
    """Test configuring a logger with a custom handler."""
    logger = logging.getLogger("test_handler")
    logger.handlers.clear()

    custom_handler = logging.FileHandler("/dev/null")
    custom_handler.setLevel(logging.WARNING)

    configure_logger(logger, handler=custom_handler)

    assert logger.handlers[0] is custom_handler
    assert logger.handlers[0].level == logging.WARNING
    assert isinstance(logger.handlers[0].formatter, RequestsEnhancedFormatter)


def test_configure_logger_with_custom_format():
    """Test configuring a logger with a custom format."""
    logger = logging.getLogger("test_format")
    logger.handlers.clear()

    custom_format = "%(levelname)s - %(message)s"
    configure_logger(logger, log_format=custom_format)

    assert logger.handlers[0].formatter._fmt == custom_format


def test_configure_logger_with_existing_formatter(stream_handler):
    """Test configuring a logger with a handler that already has a formatter."""
    logger = logging.getLogger("test_existing_formatter")
    logger.handlers.clear()

    # The fixture stream_handler already has a formatter
    configure_logger(logger, handler=stream_handler)

    # Should keep the existing formatter
    assert stream_handler.formatter._fmt == DEFAULT_LOG_FORMAT


def test_configure_logger_override_existing_formatter(stream_handler):
    """Test that explicit log_format overrides existing formatter."""
    logger = logging.getLogger("test_override_formatter")
    logger.handlers.clear()

    custom_format = "%(name)s: %(message)s"
    configure_logger(logger, handler=stream_handler, log_format=custom_format)

    # Should use the new format
    assert stream_handler.formatter._fmt == custom_format


def test_formatter_default_format():
    """Test that the formatter uses the default format when none is provided."""
    formatter = RequestsEnhancedFormatter()
    assert formatter._fmt == DEFAULT_LOG_FORMAT


def test_formatter_custom_format():
    """Test that the formatter uses a custom format when provided."""
    custom_format = "%(name)s: %(message)s"
    formatter = RequestsEnhancedFormatter(fmt=custom_format)
    assert formatter._fmt == custom_format


def test_logger_output():
    """Test that the logger outputs correctly formatted messages."""
    logger = logging.getLogger("test_output")
    logger.handlers.clear()

    # Use StringIO to capture log output
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)

    configure_logger(logger, handler=handler, log_format="%(levelname)s - %(message)s")

    logger.info("Test message")

    output = log_stream.getvalue()
    assert "INFO - Test message" in output


def test_multiple_handlers_not_duplicated():
    """Test that adding the same handler twice doesn't duplicate it."""
    logger = logging.getLogger("test_duplicate")
    logger.handlers.clear()

    handler = logging.StreamHandler()

    # Add same handler twice
    configure_logger(logger, handler=handler)
    configure_logger(logger, handler=handler)

    # Should only have one instance of the handler
    assert len(logger.handlers) == 1
    assert logger.handlers[0] is handler
