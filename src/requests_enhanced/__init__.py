"""
Requests Enhanced: A wrapper for the requests library with enhanced functionality.

This library extends the requests package with features such as:
- Automatic retries with configurable backoff
- Enhanced timeout handling
- Improved logging
- Convenient utility functions
"""

from .sessions import Session

__version__ = "0.1.4"
__all__ = ["Session"]
