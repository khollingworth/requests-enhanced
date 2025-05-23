"""
Tests for HTTP/2 connection classes in the adapters module.
"""

import pytest
from unittest.mock import patch, Mock

# Import the necessary modules
from requests_enhanced.adapters import HTTP2Adapter, HTTP2_AVAILABLE

# Import optional urllib3 components with fallback
try:
    from urllib3.poolmanager import PoolManager
except ImportError:
    # Use type ignore comments to bypass mypy errors in test files
    PoolManager = None  # type: ignore

# Skip all tests in this module if HTTP/2 is not available
pytestmark = pytest.mark.skipif(
    not HTTP2_AVAILABLE,
    reason="HTTP/2 dependencies not available (h2, hyperframe, hpack)",
)


@pytest.fixture
def mock_ssl():
    """Fixture to create a mock SSL module for testing."""
    mock = Mock()
    mock.SSLError = Exception
    return mock


@pytest.mark.skipif(not HTTP2_AVAILABLE, reason="HTTP/2 dependencies not available")
def test_http2_connection_creation():
    """Test that we can create an HTTP/2 connection."""
    adapter = HTTP2Adapter(protocol_version="h2")

    # We need to initialize the pool manager to create the necessary connection classes
    adapter.init_poolmanager(1, 1, block=False)

    # Just verify the adapter was initialized properly
    assert adapter.protocol_version == "h2"
    assert adapter.poolmanager is not None


@pytest.mark.skipif(not HTTP2_AVAILABLE, reason="HTTP/2 dependencies not available")
def test_http2_version_detection():
    """Test HTTP/2 version detection logic."""
    # Test with a mocked urllib3 version
    with patch("requests_enhanced.adapters.URLLIB3_VERSION", "2.0.0"):
        with patch("requests_enhanced.adapters.URLLIB3_MAJOR", 2):
            # Instead of mocking PoolManager which is used internally,
            # we'll just check that the adapter creates a pool manager
            adapter = HTTP2Adapter(protocol_version="h2")
            adapter.init_poolmanager(1, 1, block=False)

            # Ensure the adapter knows we're using urllib3 2.x and has a pool manager
            assert adapter.protocol_version == "h2"
            assert adapter.poolmanager is not None


@pytest.mark.skipif(not HTTP2_AVAILABLE, reason="HTTP/2 dependencies not available")
def test_http2_adapter_with_error_handling():
    """Test error handling in HTTP/2 adapter."""
    adapter = HTTP2Adapter(protocol_version="h2")

    # Patch the actual PoolManager constructor to cause an error
    original_poolmanager = PoolManager

    def pool_manager_with_error(*args, **kwargs):
        if kwargs.get("protocol") == "h2":
            raise Exception("Test error")
        return original_poolmanager(*args, **kwargs)

    with patch("urllib3.poolmanager.PoolManager", side_effect=pool_manager_with_error):
        # This should not raise an exception due to our fallback mechanisms
        adapter.init_poolmanager(1, 1, block=False)

        # Verify the adapter still has a pool manager
        assert adapter.poolmanager is not None


@pytest.mark.skipif(not HTTP2_AVAILABLE, reason="HTTP/2 dependencies not available")
def test_http2_adapter_parent_methods():
    """Test that HTTP/2 adapter inherits and uses parent adapter methods correctly."""
    adapter = HTTP2Adapter(protocol_version="h2")

    # Test that cert_verify and proxy_headers methods are available
    # These are inherited from the parent HTTPAdapter
    assert hasattr(adapter, "cert_verify")
    assert hasattr(adapter, "proxy_headers")

    # Test that we can call add_headers
    request = Mock()
    request.url = "https://example.com"
    request.headers = {}

    # This should not raise an exception
    adapter.add_headers(request)


@pytest.mark.skipif(not HTTP2_AVAILABLE, reason="HTTP/2 dependencies not available")
def test_http2_adapter_close():
    """Test HTTP/2 adapter close method."""
    adapter = HTTP2Adapter(protocol_version="h2")

    # Initialize the pool manager
    adapter.init_poolmanager(1, 1, block=False)

    # The adapter should have a pool manager
    assert adapter.poolmanager is not None

    # Mock the pool manager's clear method
    adapter.poolmanager.clear = Mock()

    # Call close
    adapter.close()

    # Verify that the pool manager's clear method was called
    adapter.poolmanager.clear.assert_called_once()
