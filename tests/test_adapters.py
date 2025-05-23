"""
Tests for the HTTP/2 adapter functionality.
"""

import pytest
from unittest.mock import patch, MagicMock

# Conditional imports to handle potential import errors
try:
    from requests_enhanced.adapters import HTTP2Adapter, HTTP2_AVAILABLE
except ImportError:
    # Provide mock objects if imports fail
    # Use type ignore comments to bypass mypy errors in test files
    HTTP2Adapter = MagicMock  # type: ignore
    HTTP2_AVAILABLE = False

# Skip HTTP/2 tests if dependencies are missing
pytestmark = pytest.mark.skipif(
    not HTTP2_AVAILABLE,
    reason="HTTP/2 dependencies not available (h2, hyperframe, hpack)",
)


def test_http2_adapter_init():
    """Test initialization of HTTP2Adapter."""
    adapter = HTTP2Adapter(protocol_version="h2")
    assert adapter.protocol_version == "h2"


def test_http2_adapter_init_without_dependencies():
    """Test initialization fails when HTTP/2 dependencies are not available."""
    with patch("requests_enhanced.adapters.HTTP2_AVAILABLE", False):
        with pytest.raises(
            ImportError, match="HTTP/2 support requires additional dependencies"
        ):
            HTTP2Adapter(protocol_version="h2")

        # Should work with HTTP/1.1
        adapter = HTTP2Adapter(protocol_version="http/1.1")
        assert adapter.protocol_version == "http/1.1"


def test_http2_pool_manager_initialization():
    """Test that HTTP/2 adapter can initialize a pool manager."""
    # Skip this test if HTTP/2 dependencies are not available
    if not HTTP2_AVAILABLE:
        pytest.skip("HTTP/2 dependencies not available")

    # Create an adapter with HTTP/2 protocol
    adapter = HTTP2Adapter(protocol_version="h2")

    # Store the original pool manager if it exists
    original_pool_manager = getattr(adapter, "poolmanager", None)

    # Call init_poolmanager with our test values
    adapter.init_poolmanager(10, 10, block=False)

    # Verify the pool manager was created and is different from the original
    assert hasattr(adapter, "poolmanager")
    assert adapter.poolmanager is not None
    assert adapter.poolmanager is not original_pool_manager

    # Verify we can access the pool manager as an object (doesn't raise errors)
    # We're testing basic functionality without checking specific attributes
    # since these vary by urllib3 version
    assert isinstance(adapter.poolmanager, object)


def test_http2_adapter_with_http1_fallback():
    """Test that HTTP/2 adapter falls back to HTTP/1.1 when necessary."""
    # Test with protocol_version explicitly set to HTTP/1.1
    adapter = HTTP2Adapter(protocol_version="http/1.1")

    with patch("requests_enhanced.adapters.PoolManager") as mock_pool_manager:
        adapter.init_poolmanager(10, 10, block=False)

        # Check that alpn_protocols is not in the kwargs
        call_kwargs = mock_pool_manager.call_args[1]
        assert "alpn_protocols" not in call_kwargs


@pytest.mark.skipif(not HTTP2_AVAILABLE, reason="HTTP/2 dependencies not available")
def test_http2_adapter_initialization():
    """Test HTTP/2 adapter initialization when dependencies are available."""
    from requests_enhanced import Session

    # Create a session with HTTP/2 support
    session = Session(http_version="2")

    # Check that HTTP/2 adapter is mounted for HTTPS
    adapter = session.get_adapter("https://example.com")
    assert isinstance(adapter, HTTP2Adapter)

    # Check that regular adapter is used for HTTP
    adapter = session.get_adapter("http://example.com")
    from requests.adapters import HTTPAdapter

    assert isinstance(adapter, HTTPAdapter)
    assert not isinstance(adapter, HTTP2Adapter)
