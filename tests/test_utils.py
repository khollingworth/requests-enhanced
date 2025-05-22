"""
Tests for the utility functions.
"""

import pytest
import requests
from unittest.mock import MagicMock

from requests_enhanced.utils import json_get, json_post
from requests_enhanced.exceptions import RequestTimeoutError


def test_json_get_successful(http_server):
    """Test successful JSON GET request."""
    expected_data = {"status": "success", "data": {"id": 123, "name": "test"}}

    # Configure server to return JSON response
    http_server.expect_request(
        "/get-test", query_string="param=value"
    ).respond_with_json(expected_data)

    # Call the utility function
    result = json_get(f"{http_server.url_for('/get-test')}", params={"param": "value"})

    # Verify response
    assert result == expected_data


def test_json_get_with_timeout():
    """Test JSON GET with timeout error."""
    # Mock a session that raises a timeout error
    mock_session = MagicMock()
    mock_session.get.side_effect = RequestTimeoutError(
        "Request timed out", original_exception=requests.exceptions.Timeout()
    )

    with pytest.raises(RequestTimeoutError) as excinfo:
        json_get("https://example.com", session=mock_session)

    assert "Request timed out" in str(excinfo.value)


def test_json_get_with_invalid_json(http_server):
    """Test JSON GET with invalid JSON response."""
    # Configure server to return invalid JSON
    http_server.expect_request("/invalid-json").respond_with_data(
        "Not a JSON response", content_type="application/json"
    )

    # Should raise ValueError due to invalid JSON
    with pytest.raises(ValueError):
        json_get(f"{http_server.url_for('/invalid-json')}")


def test_json_post_successful(http_server):
    """Test successful JSON POST request."""
    request_data = {"name": "test", "value": 42}
    expected_response = {"status": "created", "id": 123}

    # Configure server to check request and return response
    http_server.expect_request(
        "/post-test", method="POST", json=request_data
    ).respond_with_json(expected_response)

    # Call the utility function
    result = json_post(f"{http_server.url_for('/post-test')}", json=request_data)

    # Verify response
    assert result == expected_response


def test_json_post_with_custom_session():
    """Test JSON POST with a custom session."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "success"}

    mock_session = MagicMock()
    mock_session.post.return_value = mock_response

    # Call with custom session
    result = json_post(
        "https://example.com/api", json={"test": "data"}, session=mock_session
    )

    # Verify session was used
    mock_session.post.assert_called_once()
    assert result == {"status": "success"}
