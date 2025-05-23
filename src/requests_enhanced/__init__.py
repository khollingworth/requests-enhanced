"""
Requests Enhanced: A wrapper for the requests library with enhanced functionality.

This library extends the requests package with features such as:
- Automatic retries with configurable backoff
- Enhanced timeout handling
- Improved logging
- Convenient utility functions
- HTTP/2 protocol support for improved performance
- HTTP/3 protocol support with automatic fallback mechanism
- OAuth 1.0/1.1 and OAuth 2.0 authentication support
"""

from typing import Optional, Type, Any

from .sessions import Session
from .adapters import HTTP2Adapter, HTTP3Adapter, HTTP2_AVAILABLE, HTTP3_AVAILABLE

# OAuth support (optional dependency)
try:
    from .oauth import (
        OAuth1EnhancedSession,
        OAuth2EnhancedSession,
        OAuthNotAvailableError,
        OAUTH_AVAILABLE,
    )

    # If OAUTH_AVAILABLE is False, set classes to None for the test
    if not OAUTH_AVAILABLE:
        OAuth1EnhancedSession = None  # type: ignore  # noqa: F811
        OAuth2EnhancedSession = None  # type: ignore  # noqa: F811
except ImportError:
    OAUTH_AVAILABLE = False
    OAuth1EnhancedSession: Optional[Type[Any]] = None  # type: ignore
    OAuth2EnhancedSession: Optional[Type[Any]] = None  # type: ignore
    OAuthNotAvailableError: Optional[Type[Any]] = None  # type: ignore

__version__ = "1.0.0"
__all__ = [
    "Session",
    "HTTP2Adapter",
    "HTTP3Adapter",
    "HTTP2_AVAILABLE",
    "HTTP3_AVAILABLE",
    "OAuth1EnhancedSession",
    "OAuth2EnhancedSession",
    "OAUTH_AVAILABLE",
    "OAuthNotAvailableError",
]
