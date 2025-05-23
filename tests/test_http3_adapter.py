"""
Tests for HTTP/3 adapter implementation.

These tests focus on the HTTP3Adapter class and its initialization,
with focus on the fallback mechanisms from HTTP/3 to HTTP/2 to HTTP/1.1.
"""

import pytest
from unittest.mock import patch, MagicMock

# Conditional imports to handle potential import errors
try:
    from requests_enhanced.adapters import (
        HTTP3Adapter,
        HTTP3_AVAILABLE,
        HTTP2_AVAILABLE,
        URLLIB3_MAJOR,
        URLLIB3_MINOR,
    )
    from requests.packages.urllib3.poolmanager import PoolManager
except ImportError:
    # Provide mock objects if imports fail
    # Use type ignore comments to bypass mypy errors in test files
    HTTP3Adapter = MagicMock  # type: ignore
    HTTP3_AVAILABLE = False
    HTTP2_AVAILABLE = False
    URLLIB3_MAJOR = 1
    URLLIB3_MINOR = 0
    PoolManager = MagicMock  # type: ignore


def test_http3_adapter_init():
    """Test HTTP3Adapter initialization with default values."""
    adapter = HTTP3Adapter()
    # When HTTP/3 is not available, it falls back to HTTP/2
    if HTTP3_AVAILABLE:
        assert adapter.protocol_version == "h3"
    else:
        assert adapter.protocol_version == "h2"
    assert adapter.quic_connection_options is None
    assert adapter.quic_max_datagram_size == 1350


def test_http3_adapter_custom_init():
    """Test HTTP3Adapter initialization with custom values."""
    adapter = HTTP3Adapter(
        protocol_version="h3",
        quic_connection_options={"option1": "value1"},
        quic_max_datagram_size=1500,
        pool_connections=20,
        pool_maxsize=20,
    )
    # When HTTP/3 is not available, it falls back to HTTP/2
    if HTTP3_AVAILABLE:
        assert adapter.protocol_version == "h3"
    else:
        assert adapter.protocol_version == "h2"
    assert adapter.quic_connection_options == {"option1": "value1"}
    assert adapter.quic_max_datagram_size == 1500


@patch("requests_enhanced.adapters.HTTP3_AVAILABLE", False)
@patch("requests_enhanced.adapters.HTTP2_AVAILABLE", True)
def test_http3_adapter_fallback_to_http2():
    """Test HTTP3Adapter fallback to HTTP/2 when HTTP/3 is not available."""
    adapter = HTTP3Adapter(protocol_version="h3")
    assert adapter.protocol_version == "h2"


@patch("requests_enhanced.adapters.HTTP3_AVAILABLE", False)
@patch("requests_enhanced.adapters.HTTP2_AVAILABLE", False)
def test_http3_adapter_fallback_to_http1():
    """Test HTTP3Adapter fallback to HTTP/1.1.

    Tests fallback to HTTP/1.1 when HTTP/3 and HTTP/2 are not available.
    """
    adapter = HTTP3Adapter(protocol_version="h3")
    assert adapter.protocol_version == "http/1.1"


@pytest.mark.skipif(not HTTP3_AVAILABLE, reason="HTTP/3 dependencies not available")
@patch("requests_enhanced.adapters.HTTP3PoolManager")
def test_http3_adapter_init_poolmanager(mock_pool_manager):
    """Test HTTP3Adapter init_poolmanager with HTTP/3 protocol."""
    adapter = HTTP3Adapter(protocol_version="h3")
    adapter.init_poolmanager(10, 10, block=False)
    assert mock_pool_manager.called
    # The exact number of calls might vary depending on implementation details
    # We just verify it was called at least once


@patch("requests_enhanced.adapters.HTTP3_AVAILABLE", False)
@patch("requests_enhanced.adapters.HTTP2_AVAILABLE", True)
@patch("requests_enhanced.adapters.HTTP2Adapter")
def test_http3_adapter_init_poolmanager_fallback_to_http2(mock_http2_adapter):
    """Test HTTP3Adapter init_poolmanager fallback to HTTP/2."""
    mock_instance = MagicMock()
    mock_http2_adapter.return_value = mock_instance

    adapter = HTTP3Adapter(protocol_version="h3")
    adapter.init_poolmanager(10, 10, block=False)

    assert mock_http2_adapter.called
    assert mock_instance.init_poolmanager.called


@patch("requests_enhanced.adapters.HTTP3_AVAILABLE", False)
@patch("requests_enhanced.adapters.HTTP2_AVAILABLE", False)
@patch("requests_enhanced.adapters.PoolManager")
def test_http3_adapter_init_poolmanager_fallback_to_http1(mock_pool_manager):
    """Test HTTP3Adapter init_poolmanager fallback to HTTP/1.1."""
    adapter = HTTP3Adapter(protocol_version="h3")
    adapter.init_poolmanager(10, 10, block=False)
    assert mock_pool_manager.called


@patch("requests_enhanced.adapters.HTTP3_AVAILABLE", True)
def test_http3_adapter_pool_manager_error_handling():
    """Test HTTP3Adapter poolmanager error handling and fallback."""
    with patch("requests_enhanced.adapters.HTTP3PoolManager") as mock_pool_manager:
        # Simulate HTTP3PoolManager failing
        mock_pool_manager.side_effect = Exception("HTTP/3 pool error")

        # Then ensure fallback to HTTP/2 is attempted
        with patch("requests_enhanced.adapters.HTTP2Adapter") as mock_http2_adapter:
            mock_instance = MagicMock()
            mock_http2_adapter.return_value = mock_instance

            adapter = HTTP3Adapter(protocol_version="h3")
            adapter.init_poolmanager(10, 10, block=False)

            # Verify fallback
            assert mock_pool_manager.called
            assert mock_http2_adapter.called
            # The exact number of calls may vary based on implementation details
            # The important part is that HTTP2Adapter was called for fallback
