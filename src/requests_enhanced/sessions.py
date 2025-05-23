"""Enhanced session handling for requests with retry and timeout capabilities.

This module provides an enhanced Session class that extends the functionality
of the standard requests.Session with automatic retry capabilities, default timeout
settings, and improved error handling through custom exception types.

Typical usage example:
    >>> from requests_enhanced import Session
    >>> session = Session(timeout=(3, 30), max_retries=3)
    >>> response = session.get('https://api.example.com/resource')
"""

import logging
from typing import Any, Literal, Optional, Tuple, Union

import requests
from requests import Session as RequestsSession
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .adapters import HTTP2Adapter, HTTP3Adapter, HTTP2_AVAILABLE, HTTP3_AVAILABLE
from .exceptions import RequestRetryError, RequestTimeoutError

# Configure module logger
logger = logging.getLogger("requests_enhanced")


class Session(RequestsSession):
    """
    Enhanced requests Session with automatic retry and timeout handling.

    This class extends the standard requests.Session with:
    - Configurable retry mechanism with exponential backoff
    - Default timeout settings for all requests
    - Enhanced error handling with specific exception types

    Attributes:
        timeout: Default timeout value used for all requests when not explicitly
            provided
    """

    def __init__(
        self,
        retry_config: Optional[Retry] = None,
        timeout: Union[float, Tuple[float, float]] = (3.05, 30),
        max_retries: int = 3,
        http_version: Literal["1.1", "2", "3"] = "1.1",
    ) -> None:
        """
        Initialize a new Session with retry and timeout configuration.

        Args:
            retry_config: Custom Retry config. If None, a default will be created.
            timeout: Default timeout as (connect_timeout, read_timeout) tuple
                or float value. Tuple recommended for precise control.
            max_retries: Number of retries for requests (used only if retry_config
                is None). Must be a positive integer.

        Raises:
            ValueError: If max_retries is less than 1
        """
        # Validate inputs
        if max_retries < 1:
            raise ValueError("max_retries must be at least 1")

        if http_version not in ["1.1", "2", "3"]:
            raise ValueError("http_version must be either '1.1', '2', or '3'")

        super().__init__()

        # Set default timeout
        self.timeout = timeout

        # Store HTTP version for reference
        self.http_version = http_version

        # Configure retries
        if retry_config is None:
            # Reason: Create a default retry configuration with sensible defaults
            # for common server error codes and HTTP methods
            retry_config = Retry(
                total=max_retries,
                backoff_factor=0.5,  # Exponential backoff factor
                status_forcelist=[500, 502, 503, 504],  # Common server errors
                allowed_methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"],
            )

        self.setup_adapter(http_version, retry_config)

        logger.debug(
            f"Created Session with timeout={timeout}, retry_config={retry_config}, "
            f"http_version={http_version}"
        )

    def setup_adapter(self, http_version: str, retry_config: Retry) -> None:
        """Set up the appropriate adapter based on the requested HTTP version.

        Args:
            http_version: HTTP version to use ('1', '2', or '3')
            retry_config: Retry configuration to use
        """
        # Create a variable with Union type to handle different adapter types
        adapter: Union[HTTP3Adapter, HTTP2Adapter, HTTPAdapter]

        # Determine which adapter to use based on HTTP version
        if http_version == "3":
            # Try HTTP/3 adapter
            if HTTP3_AVAILABLE:
                # Use HTTP/3 adapter with automatic fallback
                adapter = HTTP3Adapter(protocol_version="h3", max_retries=retry_config)
                logger.debug("Using HTTP/3 adapter with fallback capability")
            elif HTTP2_AVAILABLE:
                # Fall back to HTTP/2 if HTTP/3 dependencies aren't available
                adapter = HTTP2Adapter(protocol_version="h2", max_retries=retry_config)
                logger.warning(
                    "HTTP/3 requested but dependencies not available. "
                    "Falling back to HTTP/2. Install HTTP/3 with: "
                    "pip install requests-enhanced[http3]"
                )
            else:
                # Final fallback to HTTP/1.1
                adapter = HTTPAdapter(max_retries=retry_config)
                logger.warning(
                    "HTTP/3 and HTTP/2 dependencies not available. "
                    "Using HTTP/1.1 instead. Install with: "
                    "pip install requests-enhanced[http3] or "
                    "pip install requests-enhanced[http2]"
                )
        elif http_version == "2":
            # Try HTTP/2 adapter
            if HTTP2_AVAILABLE:
                # Use HTTP/2 adapter for HTTPS requests
                adapter = HTTP2Adapter(protocol_version="h2", max_retries=retry_config)
                logger.debug("Using HTTP/2 adapter for HTTPS connections")
            else:
                # Fall back to HTTP/1.1
                adapter = HTTPAdapter(max_retries=retry_config)
                logger.warning(
                    "HTTP/2 requested but dependencies not available. "
                    "Using HTTP/1.1 instead. Install with: "
                    "pip install requests-enhanced[http2]"
                )
        else:
            # Standard HTTP/1.1 adapter
            adapter = HTTPAdapter(max_retries=retry_config)
            logger.debug("Using standard HTTP/1.1 adapter")

        # Mount the appropriate adapter for HTTPS URLs (potentially HTTP/2 or HTTP/3)
        self.mount("https://", adapter)

        # Use standard adapter for HTTP connections (HTTP/1.1 only)
        standard_adapter = HTTPAdapter(max_retries=retry_config)
        self.mount("http://", standard_adapter)

        logger.debug(
            f"Created Session with timeout={self.timeout}, "
            f"retry_config={retry_config}, http_version={http_version}"
        )

    # The signature is intentionally simplified from the parent class
    # while maintaining compatibility with how it's used in our codebase
    def request(  # type: ignore[override]
        self, method: str, url: str, **kwargs: Any
    ) -> requests.Response:
        """
        Send a request with enhanced error handling for timeouts and retries.

        This method overrides the standard Session.request method to provide
        improved error handling and automatic application of default timeout.

        Args:
            method: HTTP method (e.g., 'GET', 'POST', 'PUT')
            url: URL for the request
            **kwargs: Additional arguments to pass to the request, including:
                - headers: Dict of HTTP headers
                - data: Dict, list of tuples, bytes, or file-like object
                - json: Json data to send in the body
                - params: Dict or list of tuples for query parameters
                - timeout: Custom timeout for this specific request

        Returns:
            Response object with status code, headers, and content

        Raises:
            RequestTimeoutError: When the request times out
            RequestRetryError: When max retries are exceeded
            requests.exceptions.RequestException: For other request-related errors
        """
        # Early validation
        if not url:
            raise ValueError("URL cannot be empty")

        if not method:
            raise ValueError("HTTP method cannot be empty")

        # Use the default timeout if not specified in kwargs
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout

        logger.debug(f"Making {method} request to {url}")

        try:
            # Delegate to the parent class to make the actual request
            response = super().request(method, url, **kwargs)
            return response
        except requests.exceptions.Timeout as e:
            # Handle timeout exceptions with our custom error type
            timeout_val = kwargs.get("timeout", self.timeout)
            logger.error(f"Request to {url} timed out after {timeout_val} seconds")

            if "response" in locals() and response is None:
                timeout_value = kwargs.get("timeout", self.timeout)
                raise RequestTimeoutError(
                    f"Request to {url} timed out after {timeout_value} seconds"
                )
            raise RequestTimeoutError(
                f"Request to {url} timed out", original_exception=e
            )
        except requests.exceptions.RetryError as e:
            # Handle retry exhaustion with our custom error type
            logger.error(f"Max retries exceeded for request to {url}")
            raise RequestRetryError(
                f"Max retries exceeded for request to {url}", original_exception=e
            )
        except requests.exceptions.RequestException as e:
            # Log and re-raise other request exceptions
            logger.error(f"Request to {url} failed: {str(e)}")
            raise
