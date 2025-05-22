"""
Tests for the Session class functionality.
"""

import pytest
import requests
from requests.adapters import Retry

from requests_enhanced import Session
from requests_enhanced.exceptions import RequestTimeoutError, RequestRetryError


def test_session_init_defaults():
    """Test Session initialization with default values."""
    session = Session()

    # Default timeout should be set
    assert session.timeout == (3.05, 30)

    # Adapters should be mounted for both HTTP and HTTPS
    assert "http://" in session.adapters
    assert "https://" in session.adapters


def test_session_custom_timeout():
    """Test Session with custom timeout."""
    custom_timeout = (5, 60)
    session = Session(timeout=custom_timeout)
    assert session.timeout == custom_timeout


def test_session_custom_retry():
    """Test Session with custom retry configuration."""
    custom_retry = Retry(
        total=5,
        backoff_factor=1.0,
        status_forcelist=[500, 503],
        allowed_methods=["GET"],
    )
    session = Session(retry_config=custom_retry)

    # Verify the adapter has our custom retry config
    adapter = session.adapters["https://"]
    assert adapter.max_retries.total == 5
    assert adapter.max_retries.backoff_factor == 1.0
    assert adapter.max_retries.status_forcelist == [500, 503]
    # Check if allowed_methods is in the expected format
    # Different requests versions may handle this differently (list vs frozenset)
    assert "GET" in adapter.max_retries.allowed_methods


def test_session_request_with_default_timeout(
    monkeypatch, configuring_logger_for_tests
):
    """Test that requests use the default timeout if not specified."""
    # Mock the parent request method to check the timeout
    called_with_timeout = None

    def mock_request(self, method, url, **kwargs):
        nonlocal called_with_timeout
        called_with_timeout = kwargs.get("timeout")
        return requests.Response()

    monkeypatch.setattr(requests.Session, "request", mock_request)

    session = Session(timeout=(10, 20))
    session.get("https://example.com")

    assert called_with_timeout == (10, 20)


def test_session_timeout_error(monkeypatch, configuring_logger_for_tests):
    """Test that timeout errors are converted to RequestTimeoutError."""

    # Mock the request to raise a Timeout
    def mock_request(self, method, url, **kwargs):
        raise requests.exceptions.Timeout("Connection timed out")

    monkeypatch.setattr(requests.Session, "request", mock_request)

    session = Session()

    with pytest.raises(RequestTimeoutError) as excinfo:
        session.get("https://example.com")

    # Check error message
    assert "Request to https://example.com timed out" in str(excinfo.value)
    # Check original exception is stored
    assert isinstance(excinfo.value.original_exception, requests.exceptions.Timeout)
    # Check log entry
    assert (
        "Request to https://example.com timed out"
        in configuring_logger_for_tests.getvalue()
    )


def test_session_retry_error(monkeypatch, configuring_logger_for_tests):
    """Test that retry errors are converted to RequestRetryError."""

    # Mock the request to raise a RetryError
    def mock_request(self, method, url, **kwargs):
        raise requests.exceptions.RetryError("Max retries exceeded")

    monkeypatch.setattr(requests.Session, "request", mock_request)

    session = Session()

    with pytest.raises(RequestRetryError) as excinfo:
        session.get("https://example.com")

    # Check error message
    assert "Max retries exceeded for request to https://example.com" in str(
        excinfo.value
    )
    # Check original exception is stored
    assert isinstance(excinfo.value.original_exception, requests.exceptions.RetryError)
    # Check log entry
    assert (
        "Max retries exceeded for request to https://example.com"
        in configuring_logger_for_tests.getvalue()
    )


def test_invalid_input_validation():
    """Test validation of input parameters."""
    # Test invalid max_retries value
    with pytest.raises(ValueError, match="max_retries must be at least 1"):
        Session(max_retries=0)

    with pytest.raises(ValueError, match="max_retries must be at least 1"):
        Session(max_retries=-1)


def test_request_input_validation(monkeypatch, configuring_logger_for_tests):
    """Test validation of request method inputs."""
    session = Session()

    # Test empty URL
    with pytest.raises(ValueError, match="URL cannot be empty"):
        session.get("")

    # Test empty method - need to use request directly as the convenience methods
    # like get(), post() always provide a method
    with pytest.raises(ValueError, match="HTTP method cannot be empty"):
        session.request("", "https://example.com")


def test_generic_request_exception(monkeypatch, configuring_logger_for_tests):
    """Test handling of general RequestException errors."""

    # Mock the request to raise a generic RequestException
    def mock_request(self, method, url, **kwargs):
        raise requests.exceptions.RequestException("Generic error")

    monkeypatch.setattr(requests.Session, "request", mock_request)

    session = Session()

    # Should re-raise the original exception
    with pytest.raises(requests.exceptions.RequestException):
        session.get("https://example.com")

    # Check log entry was created
    assert (
        "Request to https://example.com failed: Generic error"
        in configuring_logger_for_tests.getvalue()
    )


def test_session_retry_limit_exceeded(http_server, configuring_logger_for_tests):
    """Test that max retries are actually enforced."""
    # Configure server to always return 503 status code
    http_server.expect_request("/test").respond_with_data(
        "Service Unavailable", status=503
    )

    # Create session with minimal retry configuration
    retry_config = Retry(
        total=1, backoff_factor=0, status_forcelist=[503], allowed_methods=["GET"]
    )
    session = Session(retry_config=retry_config)

    # Request should fail after retries
    with pytest.raises(RequestRetryError):
        session.get(f"{http_server.url_for('/test')}")

    # Verify retries were attempted in logs
    log_content = configuring_logger_for_tests.getvalue()
    assert "Retry(total=1" in log_content
