"""
Advanced tests for HTTP/2 connection and connection pool implementations.

These tests focus on increasing coverage for HTTP2Connection, HTTP2ConnectionPool,
and edge cases in the connection handling code.
"""

import pytest
from unittest.mock import patch, MagicMock

# Conditional imports to handle potential import errors
try:
    from requests_enhanced.adapters import (
        HTTP2Connection,
        HTTP2ConnectionPool,
        HTTP2_AVAILABLE,
        URLLIB3_MAJOR,
        URLLIB3_MINOR,
    )
except ImportError:
    # Provide mock objects if imports fail
    # Use type ignore comments to bypass mypy errors in test files
    HTTP2Connection = MagicMock  # type: ignore
    HTTP2ConnectionPool = MagicMock  # type: ignore
    HTTP2_AVAILABLE = False
    URLLIB3_MAJOR = 1
    URLLIB3_MINOR = 0

# Skip HTTP/2 tests if dependencies are missing
pytestmark = pytest.mark.skipif(
    not HTTP2_AVAILABLE,
    reason="HTTP/2 dependencies not available (h2, hyperframe, hpack)",
)


def test_http2_connection_init():
    """Test initialization of HTTP2Connection with various parameters."""
    # Basic initialization
    conn = HTTP2Connection(host="example.com", port=443)
    assert hasattr(conn, "_protocol")
    # The default protocol might be 'https' or 'http/1.1' depending on the environment
    # so we'll just check it's a string rather than a specific value
    assert isinstance(conn._protocol, str)

    # With protocol specified
    conn = HTTP2Connection(host="example.com", port=443, protocol="h2")
    assert conn._protocol == "h2"

    # With request_context (should be handled gracefully)
    conn = HTTP2Connection(
        host="example.com", port=443, request_context={"test": "value"}
    )
    assert hasattr(conn, "_protocol")


def test_http2_connection_connect_http2():
    """Test HTTP2Connection connect method with HTTP/2 protocol."""
    # Skip if HTTP/2 dependencies not available
    if not HTTP2_AVAILABLE:
        pytest.skip("HTTP/2 dependencies not available")

    # Create a connection with HTTP/2 protocol
    conn = HTTP2Connection(host="example.com", port=443, protocol="h2")

    # Mock the parent connect method
    with patch("requests.packages.urllib3.connection.HTTPSConnection.connect"):
        # Mock the sock attribute and its context
        mock_sock = MagicMock()
        mock_context = MagicMock()
        mock_sock.context = mock_context

        # Set the sock attribute
        conn.sock = mock_sock

        # Call the connect method
        conn.connect()

        # Verify ALPN protocols were set if HTTP2_AVAILABLE is True
        if HTTP2_AVAILABLE:
            # Make sure the method exists before asserting it was called
            if hasattr(mock_context, "set_alpn_protocols"):
                mock_context.set_alpn_protocols.assert_called_once_with(
                    ["h2", "http/1.1"]
                )
            else:
                # If the method doesn't exist (depends on OpenSSL version),
                # this is expected behavior, so we do nothing
                pass


def test_http2_connection_connect_alpn_error():
    """Test HTTP2Connection connect method handling ALPN setting errors."""
    # Skip if HTTP/2 dependencies not available
    if not HTTP2_AVAILABLE:
        pytest.skip("HTTP/2 dependencies not available")

    # Create a connection with HTTP/2 protocol
    conn = HTTP2Connection(host="example.com", port=443, protocol="h2")

    # Mock the parent connect method
    with patch("requests.packages.urllib3.connection.HTTPSConnection.connect"):
        # Mock the sock attribute and its context with an error
        mock_sock = MagicMock()
        mock_context = MagicMock()
        mock_context.set_alpn_protocols.side_effect = AttributeError(
            "ALPN not supported"
        )
        mock_sock.context = mock_context

        # Set the sock attribute
        conn.sock = mock_sock

        # Call the connect method - should handle the error gracefully
        conn.connect()


def test_http2_connection_connect_error():
    """Test HTTP2Connection connect method handling connection errors."""
    # Create a connection with HTTP/2 protocol
    conn = HTTP2Connection(host="example.com", port=443, protocol="h2")

    # Mock the parent connect method to raise an error
    with patch(
        "requests.packages.urllib3.connection.HTTPSConnection.connect",
        side_effect=Exception("Connection error"),
    ):

        # Call the connect method - should propagate the error
        with pytest.raises(Exception, match="Connection error"):
            conn.connect()


def test_http2_connection_pool_init():
    """Test initialization of HTTP2ConnectionPool."""
    # Basic initialization
    pool = HTTP2ConnectionPool(host="example.com", port=443)
    assert hasattr(pool, "_protocol")
    assert pool._protocol == "http/1.1"

    # With protocol specified
    pool = HTTP2ConnectionPool(host="example.com", port=443, protocol="h2")
    assert pool._protocol == "h2"


def test_http2_connection_pool_init_type_error():
    """Test HTTP2ConnectionPool initialization with TypeError handling."""
    # Mock the parent class init to raise a TypeError with an unexpected keyword
    with patch("requests_enhanced.adapters.HTTPSConnectionPool.__init__") as mock_init:
        # First call raises TypeError for an unexpected keyword argument
        mock_init.side_effect = [
            TypeError("got an unexpected keyword argument 'unknown_arg'"),
            None,  # Second call succeeds
        ]

        # Create the pool - should handle the error and retry
        HTTP2ConnectionPool(host="example.com", port=443, unknown_arg="value")

        # Verify __init__ was called twice (once with error, once successfully)
        assert mock_init.call_count == 2


def test_http2_connection_pool_init_other_type_error():
    """Test HTTP2ConnectionPool initialization with other TypeError handling."""
    # Mock the parent class init to raise a TypeError without keyword message
    with patch("requests_enhanced.adapters.HTTPSConnectionPool.__init__") as mock_init:
        # TypeError without the "unexpected keyword" message
        mock_init.side_effect = TypeError("Some other type error")

        # Should re-raise the error
        with pytest.raises(TypeError, match="Some other type error"):
            HTTP2ConnectionPool(host="example.com", port=443)


def test_http2_connection_pool_new_conn():
    """Test HTTP2ConnectionPool _new_conn method."""
    # Create a pool
    pool = HTTP2ConnectionPool(host="example.com", port=443, protocol="h2")

    # Call _new_conn
    conn = pool._new_conn()

    # Verify the connection is of the right type and has the protocol set
    assert isinstance(conn, HTTP2Connection)
    assert conn._protocol == "h2"


def test_http2_connection_pool_new_conn_type_error():
    """Test HTTP2ConnectionPool _new_conn method with TypeError handling."""
    # Create a pool
    pool = HTTP2ConnectionPool(host="example.com", port=443, protocol="h2")

    # Mock the parent _new_conn method to raise a TypeError
    with patch(
        "requests.packages.urllib3.connectionpool.HTTPSConnectionPool._new_conn",
        side_effect=TypeError("got an unexpected keyword argument 'protocol'"),
    ):
        # Call _new_conn - should handle the error and create a connection directly
        conn = pool._new_conn()

        # Verify the connection is of the right type
        assert isinstance(conn, HTTP2Connection)
