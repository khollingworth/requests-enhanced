"""
Tests for HTTP/3 connection implementation.

These tests focus on the HTTP3Connection and HTTP3ConnectionPool classes,
including connection establishment and fallback mechanisms.
"""

import pytest
import ssl
from unittest.mock import patch, MagicMock

# Conditional imports to handle potential import errors
try:
    from requests_enhanced.adapters import (
        HTTP3Connection,
        HTTP3ConnectionPool,
        HTTP3_AVAILABLE,
    )
except ImportError:
    # Provide mock objects if imports fail
    # Use type ignore comments to bypass mypy errors in test files
    HTTP3Connection = MagicMock  # type: ignore
    HTTP3ConnectionPool = MagicMock  # type: ignore
    HTTP3_AVAILABLE = False


# Skip HTTP/3 tests if dependencies are missing
pytestmark = pytest.mark.skipif(
    not HTTP3_AVAILABLE,
    reason="HTTP/3 dependencies not available (aioquic, asyncio)",
)


def test_http3_connection_init():
    """Test HTTP3Connection initialization with default values."""
    conn = HTTP3Connection("example.com", 443)
    assert conn.host == "example.com"
    assert conn.port == 443
    assert conn.secure is True
    assert conn.quic_connection_options is None
    assert conn.quic_max_datagram_size == 1350


def test_http3_connection_custom_init():
    """Test HTTP3Connection initialization with custom values."""
    conn = HTTP3Connection(
        "example.com",
        443,
        quic_connection_options={"option1": "value1"},
        quic_max_datagram_size=1500,
    )
    assert conn.host == "example.com"
    assert conn.port == 443
    assert conn.quic_connection_options == {"option1": "value1"}
    assert conn.quic_max_datagram_size == 1500


def test_http3_connection_ssl_context():
    """Test HTTP3Connection creates and configures SSL context correctly."""
    # Create a connection with no SSL context
    conn = HTTP3Connection("example.com", 443)

    # Verify that an SSL context was created
    assert conn.ssl_context is not None
    assert isinstance(conn.ssl_context, ssl.SSLContext)


@patch("ssl.SSLContext.set_alpn_protocols")
def test_http3_connection_alpn_protocols(mock_set_alpn):
    """Test HTTP3Connection sets ALPN protocols with h3 as primary."""
    # Create connection and verify ALPN protocols were set correctly
    # No need to store the connection when we're only testing the mock
    HTTP3Connection("example.com", 443)
    mock_set_alpn.assert_called_once_with(["h3", "h2", "http/1.1"])


@patch("requests_enhanced.adapters.HTTP3_AVAILABLE", True)
def test_http3_connection_connect():
    """Test HTTP3Connection connect method attempts HTTP/3 connection."""
    conn = HTTP3Connection("example.com", 443)

    # Mock the superclass connect method
    with patch(
        "requests.packages.urllib3.connection.HTTPSConnection.connect"
    ) as mock_connect:
        # Create a mock socket
        mock_sock = MagicMock()
        mock_sock.selected_alpn_protocol.return_value = "h3"

        # Set the mock socket
        with patch.object(conn, "sock", mock_sock):
            conn.connect()

            # Verify that superclass connect was called
            mock_connect.assert_called_once()

            # Verify that ALPN protocol was checked
            mock_sock.selected_alpn_protocol.assert_called_once()


@patch("requests_enhanced.adapters.HTTP3_AVAILABLE", True)
def test_http3_connection_connect_fallback():
    """Test HTTP3Connection connect method falls back when h3 not selected."""
    conn = HTTP3Connection("example.com", 443)

    # Mock the superclass connect method
    with patch(
        "requests.packages.urllib3.connection.HTTPSConnection.connect"
    ) as mock_connect:
        # Create a mock socket that returns h2 instead of h3
        mock_sock = MagicMock()
        mock_sock.selected_alpn_protocol.return_value = "h2"

        # Set the mock socket
        with patch.object(conn, "sock", mock_sock):
            conn.connect()

            # Verify that superclass connect was called twice:
            # Once for HTTP/3 attempt and once for fallback
            assert mock_connect.call_count == 2

            # Verify that ALPN protocol was checked
            mock_sock.selected_alpn_protocol.assert_called_once()


@patch("requests_enhanced.adapters.HTTP3_AVAILABLE", False)
def test_http3_connection_connect_http3_not_available():
    """Test HTTP3Connection connect method falls back when HTTP/3 not available."""
    conn = HTTP3Connection("example.com", 443)

    # Mock the superclass connect method
    with patch(
        "requests.packages.urllib3.connection.HTTPSConnection.connect"
    ) as mock_connect:
        conn.connect()

        # Verify that superclass connect was called once for fallback
        mock_connect.assert_called_once()


def test_http3_connection_connect_exception_handling():
    """Test HTTP3Connection connect method handles exceptions correctly."""
    conn = HTTP3Connection("example.com", 443)

    # Mock the superclass connect method to raise an exception on first call
    with patch(
        "requests.packages.urllib3.connection.HTTPSConnection.connect"
    ) as mock_connect:
        mock_connect.side_effect = [Exception("Connection error"), None]

        # This should not raise an exception due to fallback
        conn.connect()

        # Verify that superclass connect was called twice
        assert mock_connect.call_count == 2


def test_http3_connectionpool_init():
    """Test HTTP3ConnectionPool initialization."""
    pool = HTTP3ConnectionPool("example.com", 443)
    assert pool.host == "example.com"
    assert pool.port == 443
    # After our fix, the ConnectionCls should be HTTP3Connection
    assert pool.ConnectionCls is HTTP3Connection
    assert pool.quic_connection_options is None
    assert pool.quic_max_datagram_size == 1350


def test_http3_connectionpool_custom_init():
    """Test HTTP3ConnectionPool initialization with custom options."""
    pool = HTTP3ConnectionPool(
        "example.com",
        443,
        quic_connection_options={"option1": "value1"},
        quic_max_datagram_size=1500,
    )
    assert pool.host == "example.com"
    assert pool.port == 443
    assert pool.quic_connection_options == {"option1": "value1"}
    assert pool.quic_max_datagram_size == 1500


def test_http3_connectionpool_new_conn():
    """Test HTTP3ConnectionPool _new_conn method creates HTTP3Connection correctly."""
    # Mock HTTP3Connection to avoid actual connection attempts
    with patch("requests_enhanced.adapters.HTTP3Connection") as mock_conn_cls:
        # Setup mock connection
        mock_conn = MagicMock()
        mock_conn_cls.return_value = mock_conn

        # Create connection pool with test options
        pool = HTTP3ConnectionPool(
            "example.com",
            443,
            quic_connection_options={"option1": "value1"},
            quic_max_datagram_size=1500,
        )

        # Explicitly set ConnectionCls to our mock
        pool.ConnectionCls = mock_conn_cls

        # Call _new_conn and verify the connection class was called correctly
        pool._new_conn()

        # Verify the connection class was called with the right arguments
        assert mock_conn_cls.called
        # ConnectionCls should have been called with host and port at minimum
        call_args = mock_conn_cls.call_args[1]
        assert call_args["host"] == "example.com"
        assert call_args["port"] == 443
