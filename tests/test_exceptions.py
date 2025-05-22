"""
Tests for the custom exceptions functionality.
"""

from requests_enhanced.exceptions import (
    RequestsEnhancedError,
    RequestRetryError,
    RequestTimeoutError,
    MaxRetriesExceededError,
)


def test_exceptions_init():
    """Test basic initialization of exceptions."""
    # Test base exception
    base_exc = RequestsEnhancedError("Base error")
    assert str(base_exc) == "Base error"
    assert base_exc.original_exception is None

    # Test with original exception
    original = ValueError("Original error")
    base_exc_with_original = RequestsEnhancedError(
        "With original", original_exception=original
    )
    assert base_exc_with_original.original_exception is original


def test_retry_error():
    """Test RequestRetryError initialization."""
    error = RequestRetryError("Retry error")
    assert str(error) == "Retry error"
    assert error.original_exception is None

    # With original exception
    original = ValueError("Original")
    error_with_original = RequestRetryError(
        "With original", original_exception=original
    )
    assert error_with_original.original_exception is original


def test_timeout_error():
    """Test RequestTimeoutError initialization."""
    error = RequestTimeoutError("Timeout error")
    assert str(error) == "Timeout error"
    assert error.original_exception is None

    # With original exception
    original = ValueError("Original")
    error_with_original = RequestTimeoutError(
        "With original", original_exception=original
    )
    assert error_with_original.original_exception is original


def test_max_retries_exceeded_error():
    """Test MaxRetriesExceededError initialization."""
    # Test specifically the lines that were uncovered
    original = ValueError("Original error")
    error = MaxRetriesExceededError("Max retries exceeded", original_exception=original)
    assert str(error) == "Max retries exceeded"
    assert error.original_exception is original

    # Test without original exception
    error_without_original = MaxRetriesExceededError("No original")
    assert error_without_original.original_exception is None
