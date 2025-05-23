"""
Requests Enhanced: A wrapper for the requests library with enhanced functionality.

This library extends the requests package with features such as:
- Automatic retries with configurable backoff
- Enhanced timeout handling
- Improved logging
- Convenient utility functions
- HTTP/2 protocol support for improved performance
- HTTP/3 protocol support with automatic fallback mechanism
"""

from .sessions import Session
from .adapters import HTTP2Adapter, HTTP2_AVAILABLE, HTTP3Adapter, HTTP3_AVAILABLE

__version__ = "0.1.13"
__all__ = [
    "Session",
    "HTTP2Adapter",
    "HTTP2_AVAILABLE",
    "HTTP3Adapter",
    "HTTP3_AVAILABLE",
]
