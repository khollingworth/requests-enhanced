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

from .sessions import Session
from .adapters import HTTP2Adapter, HTTP2_AVAILABLE, HTTP3Adapter, HTTP3_AVAILABLE

# OAuth support (optional dependency)
try:
    from .oauth import (
        OAuth1EnhancedSession,
        OAuth2EnhancedSession,
        OAUTH_AVAILABLE,
        OAuthNotAvailableError
    )
except ImportError:
    OAUTH_AVAILABLE = False
    OAuth1EnhancedSession = None
    OAuth2EnhancedSession = None
    OAuthNotAvailableError = None

__version__ = "0.2.0"
__all__ = [
    "Session",
    "HTTP2Adapter",
    "HTTP2_AVAILABLE", 
    "HTTP3Adapter",
    "HTTP3_AVAILABLE",
    "OAuth1EnhancedSession",
    "OAuth2EnhancedSession",
    "OAUTH_AVAILABLE",
    "OAuthNotAvailableError",
]
