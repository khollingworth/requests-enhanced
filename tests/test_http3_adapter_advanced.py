"""Advanced tests for HTTP/3 adapter functionality.

This module contains more complex tests for the HTTP3Adapter class, focusing on
edge cases, error handling, and specific behaviors that aren't covered by the
basic test suite.
"""

import socket
import pytest
from unittest.mock import patch, MagicMock
from urllib3.exceptions import MaxRetryError, NewConnectionError

from requests_enhanced.adapters import (
    HTTP3Adapter,
    HTTP3Connection,
    HTTP3_AVAILABLE,
)

# The exception classes are imported but not directly used in the test file.
# We keep them here for documentation and potential future use.


@pytest.mark.skipif(not HTTP3_AVAILABLE, reason="HTTP/3 dependencies not available")
@patch("requests_enhanced.adapters.HTTP3_AVAILABLE", True)
def test_http3_adapter_get_connection_with_tls_context():
    """Test HTTP3Adapter get_connection_with_tls_context method works correctly."""
    adapter = HTTP3Adapter(protocol_version="h3")

    with patch.object(adapter, "poolmanager") as mock_poolmanager:
        # Setup the mock
        mock_connection = MagicMock()
        mock_poolmanager.connection_from_host.return_value = mock_connection

        # Create a mock request
        mock_request = MagicMock()
        mock_request.url = "https://example.com"

        # Mock the build_connection_pool_key_attributes method
        with patch.object(
            adapter, "build_connection_pool_key_attributes"
        ) as mock_build:
            # Set up the mock to return host params and pool kwargs
            mock_build.return_value = ({"host": "example.com", "port": 443}, {})

            # Call the new method
            conn = adapter.get_connection_with_tls_context(mock_request, verify=True)

        # Verify
        assert conn == mock_connection
        mock_poolmanager.connection_from_host.assert_called_once()


@pytest.mark.skipif(not HTTP3_AVAILABLE, reason="HTTP/3 dependencies not available")
@patch("requests_enhanced.adapters.HTTP3_AVAILABLE", True)
def test_http3_adapter_proxy_manager_for():
    """Test HTTP3Adapter proxy_manager_for raises NotImplementedError."""
    adapter = HTTP3Adapter(protocol_version="h3")

    # HTTP/3 doesn't support proxies yet
    with pytest.raises(NotImplementedError):
        adapter.proxy_manager_for("http://proxy.example.com")


@pytest.mark.skipif(not HTTP3_AVAILABLE, reason="HTTP/3 dependencies not available")
@patch("requests_enhanced.adapters.HTTP3_AVAILABLE", True)
def test_http3_adapter_cert_verify():
    """Test HTTP3Adapter cert_verify method works correctly."""
    adapter = HTTP3Adapter(protocol_version="h3")

    # Create a mock connection with necessary attributes
    mock_conn = MagicMock()
    mock_conn.cert_reqs = MagicMock()
    mock_conn.ca_certs = None
    mock_conn.ca_cert_dir = None

    # Test cert_verify with a valid certificate that won't be checked for existence
    adapter.cert_verify(mock_conn, "https://example.com", True, None)

    # Verify cert settings were applied for HTTPS with verify=True and no cert
    assert mock_conn.cert_reqs == "CERT_REQUIRED"
    assert mock_conn.ca_certs is None
    assert mock_conn.ca_cert_dir is None


@pytest.mark.skipif(not HTTP3_AVAILABLE, reason="HTTP/3 dependencies not available")
@patch("requests_enhanced.adapters.HTTP3_AVAILABLE", True)
def test_http3_adapter_build_response():
    """Test HTTP3Adapter build_response method works correctly."""
    adapter = HTTP3Adapter(protocol_version="h3")

    # Create mock request and response
    mock_request = MagicMock()
    mock_request.url = "https://example.com"

    # Create a proper mock response with required attributes
    mock_resp = MagicMock()
    mock_resp.headers = {"Content-Type": "text/html"}
    mock_resp.status = 200
    mock_resp.reason = "OK"
    mock_resp.data = b"response data"

    # Use the parent class's build_response method
    with patch("requests.adapters.HTTPAdapter.build_response") as mock_build:
        mock_response = MagicMock()
        mock_build.return_value = mock_response

        response = adapter.build_response(mock_request, mock_resp)

        assert response == mock_response
        mock_build.assert_called_once_with(mock_request, mock_resp)


@pytest.mark.skipif(not HTTP3_AVAILABLE, reason="HTTP/3 dependencies not available")
@patch("requests_enhanced.adapters.HTTP3_AVAILABLE", True)
def test_http3_adapter_send_special_error_handling():
    """Test HTTP3Adapter send method with special error handling cases."""
    adapter = HTTP3Adapter(protocol_version="h3")

    # Create a mock request
    mock_request = MagicMock()
    mock_request.url = "https://example.com"

    # Test MaxRetryError handling
    with patch.object(adapter, "poolmanager") as mock_poolmanager:
        # Create a more complete mock pool with urlopen method
        mock_pool = MagicMock()
        mock_pool.urlopen.side_effect = MaxRetryError(
            pool=mock_pool, url="https://example.com", reason="Max retries exceeded"
        )
        mock_poolmanager.connection_from_url.return_value = mock_pool

        # The parent send method should handle the MaxRetryError
        with patch("requests.adapters.HTTPAdapter.send") as mock_parent_send:
            mock_parent_send.side_effect = MaxRetryError(
                pool=mock_pool, url="https://example.com", reason="Max retries exceeded"
            )

            with pytest.raises(MaxRetryError):
                adapter.send(mock_request)

    # Test NewConnectionError handling
    with patch.object(adapter, "poolmanager") as mock_poolmanager:
        mock_pool = MagicMock()
        # NewConnectionError takes 'pool' parameter
        mock_pool.urlopen.side_effect = NewConnectionError(
            pool=mock_pool, message="Failed to establish a new connection"
        )
        mock_poolmanager.connection_from_url.return_value = mock_pool

        with patch("requests.adapters.HTTPAdapter.send") as mock_parent_send:
            mock_parent_send.side_effect = NewConnectionError(
                pool=mock_pool, message="Failed to establish a new connection"
            )

            with pytest.raises(NewConnectionError):
                adapter.send(mock_request)


def test_http3_adapter_close():
    """Test HTTP3Adapter close method clears pool managers."""
    adapter = HTTP3Adapter()

    # Mock poolmanager and proxy
    adapter.poolmanager = MagicMock()
    adapter.poolmanager.clear = MagicMock()
    adapter.proxy_manager = {"http": MagicMock(), "https": MagicMock()}
    adapter.proxy_manager["http"].clear = MagicMock()
    adapter.proxy_manager["https"].clear = MagicMock()

    # Call close
    adapter.close()

    # Verify managers were cleared
    adapter.poolmanager.clear.assert_called_once()
    adapter.proxy_manager["http"].clear.assert_called_once()
    adapter.proxy_manager["https"].clear.assert_called_once()


@pytest.mark.skipif(not HTTP3_AVAILABLE, reason="HTTP/3 dependencies not available")
@patch("requests_enhanced.adapters.HTTP3_AVAILABLE", True)
def test_http3_connection_ssl_context_with_cert():
    """Test HTTP3Connection ssl_context with certificate."""
    with patch("requests_enhanced.adapters.ssl") as mock_ssl:
        # Create a mock SSL context
        mock_context = MagicMock()
        mock_ssl.create_default_context.return_value = mock_context

        # Create connection with cert
        conn = HTTP3Connection(
            host="example.com", port=443, cert_file="cert.pem", key_file="key.pem"
        )

        # Access ssl_context property to trigger creation
        context = conn.ssl_context

        # Verify SSL context was created with cert
        assert context == mock_context


@pytest.mark.skipif(not HTTP3_AVAILABLE, reason="HTTP/3 dependencies not available")
@patch("requests_enhanced.adapters.HTTP3_AVAILABLE", True)
def test_http3_connection_connect_exception_handling():
    """Test HTTP3Connection connect exception handling for different error types."""
    # Create a connection
    conn = HTTP3Connection(host="example.com", port=443)

    # Mock the parent connect method to raise TimeoutError
    with patch(
        "requests.packages.urllib3.connection.HTTPSConnection.connect"
    ) as mock_connect:
        mock_connect.side_effect = TimeoutError("Connection timed out")

        # This should raise the TimeoutError after logging
        with pytest.raises(TimeoutError):
            conn.connect()

    # Test with socket error
    with patch(
        "requests.packages.urllib3.connection.HTTPSConnection.connect"
    ) as mock_connect:
        mock_connect.side_effect = socket.error("Connection refused")

        with pytest.raises(socket.error):
            conn.connect()

    # Test with generic exception
    with patch(
        "requests.packages.urllib3.connection.HTTPSConnection.connect"
    ) as mock_connect:
        mock_connect.side_effect = Exception("Unknown error")

        with pytest.raises(Exception):
            conn.connect()
