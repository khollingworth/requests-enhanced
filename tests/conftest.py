"""
Pytest fixtures for requests-enhanced tests.
"""
import logging
import io
import pytest
from pytest_httpserver import HTTPServer

from requests_enhanced.logging import RequestsEnhancedFormatter, DEFAULT_LOG_FORMAT


@pytest.fixture
def configuring_logger_for_tests():
    """Return a StringIO object that has been configured as a log handler."""
    log_stream = io.StringIO()
    logger = logging.getLogger("requests_enhanced")
    
    # Save original handlers to restore later
    original_handlers = logger.handlers.copy()
    original_level = logger.level
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Configure with a StreamHandler that writes to StringIO
    handler = logging.StreamHandler(log_stream)
    formatter = RequestsEnhancedFormatter(DEFAULT_LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    yield log_stream
    
    # Restore original state
    logger.handlers.clear()
    for handler in original_handlers:
        logger.addHandler(handler)
    logger.setLevel(original_level)


@pytest.fixture
def stream_handler():
    """Return a StreamHandler already configured with RequestsEnhancedFormatter."""
    handler = logging.StreamHandler()
    formatter = RequestsEnhancedFormatter(DEFAULT_LOG_FORMAT)
    handler.setFormatter(formatter)
    return handler


@pytest.fixture
def http_server(request):
    """Create and start an HTTP server for testing requests."""
    server = HTTPServer()
    server.start()
    
    request.addfinalizer(server.stop)
    return server