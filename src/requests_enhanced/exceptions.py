"""
Custom exceptions for the requests-enhanced library.
"""

from typing import Optional


class RequestsEnhancedError(Exception):
    """Base exception for all requests-enhanced errors."""

    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        """
        Initialize with a message and optional original exception.

        Args:
            message: Error message
            original_exception: The original exception that caused this error
        """
        super().__init__(message)
        self.original_exception = original_exception


class RequestRetryError(RequestsEnhancedError):
    """Raised when max retries are exceeded."""

    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        """
        Initialize with a message and optional original exception.

        Args:
            message: Error message
            original_exception: The original exception that caused this error
        """
        super().__init__(message)
        self.original_exception = original_exception


class RequestTimeoutError(RequestsEnhancedError):
    """Raised when a request times out."""

    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        """
        Initialize with a message and optional original exception.

        Args:
            message: Error message
            original_exception: The original exception that caused this error
        """
        super().__init__(message)
        self.original_exception = original_exception


class MaxRetriesExceededError(RequestRetryError):
    """Raised when the maximum number of retries is exceeded."""

    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        """
        Initialize with a message and optional original exception.

        Args:
            message: Error message
            original_exception: The original exception that caused this error
        """
        super().__init__(message)
        self.original_exception = original_exception
