"""
Utility functions for simplifying common HTTP request patterns.
"""

from typing import Any, Dict, Optional

from .sessions import Session


def json_get(
    url: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any
) -> Dict[str, Any]:
    """
    Make a GET request and return the JSON response.

    Args:
        url: The URL to request
        params: Optional query parameters
        **kwargs: Additional arguments to pass to the request

    Returns:
        Parsed JSON response as a dictionary

    Raises:
        RequestTimeoutError: When the request times out
        RequestRetryError: When max retries are exceeded
        ValueError: When the response is not valid JSON
    """
    session = kwargs.pop("session", None) or Session()
    response = session.get(url, params=params, **kwargs)
    response.raise_for_status()
    return response.json()


def json_post(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Make a POST request with JSON data and return the JSON response.

    Args:
        url: The URL to request
        data: Optional form data
        json: Optional JSON data
        **kwargs: Additional arguments to pass to the request

    Returns:
        Parsed JSON response as a dictionary

    Raises:
        RequestTimeoutError: When the request times out
        RequestRetryError: When max retries are exceeded
        ValueError: When the response is not valid JSON
    """
    session = kwargs.pop("session", None) or Session()
    response = session.post(url, data=data, json=json, **kwargs)
    response.raise_for_status()
    return response.json()
