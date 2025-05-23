"""
Advanced tests for HTTP/2 adapter implementation.

These tests focus on increasing coverage for HTTP2Adapter,
particularly the init_poolmanager method and HTTP2PoolManager inner class.
"""

import pytest
from unittest.mock import patch, MagicMock

# Conditional imports to handle potential import errors
try:
    from requests_enhanced.adapters import (
        HTTP2Adapter,
        HTTP2_AVAILABLE,
        URLLIB3_MAJOR,
        URLLIB3_MINOR,
    )
    from requests.packages.urllib3.poolmanager import PoolManager
    from requests.packages.urllib3.connectionpool import (
        HTTPConnectionPool,
        HTTPSConnectionPool,
    )
except ImportError:
    # Provide mock objects if imports fail
    # Use type ignore comments to bypass mypy errors in test files
    HTTP2Adapter = MagicMock  # type: ignore
    HTTP2_AVAILABLE = False
    URLLIB3_MAJOR = 1
    URLLIB3_MINOR = 0
    PoolManager = MagicMock  # type: ignore
    HTTPConnectionPool = MagicMock  # type: ignore
    HTTPSConnectionPool = MagicMock  # type: ignore

# Skip HTTP/2 tests if dependencies are missing
pytestmark = pytest.mark.skipif(
    not HTTP2_AVAILABLE,
    reason="HTTP/2 dependencies not available (h2, hyperframe, hpack)",
)


def test_http2_adapter_init_poolmanager_http2():
    """Test HTTP2Adapter init_poolmanager with HTTP/2 protocol."""
    # Create an adapter with HTTP/2 protocol
    adapter = HTTP2Adapter(protocol_version="h2")

    # Call init_poolmanager
    adapter.init_poolmanager(10, 10, block=False)

    # Verify poolmanager was created
    assert hasattr(adapter, "poolmanager")
    assert adapter.poolmanager is not None


def test_http2_adapter_init_poolmanager_http1():
    """Test HTTP2Adapter init_poolmanager with HTTP/1.1 protocol."""
    # Create an adapter with HTTP/1.1 protocol
    adapter = HTTP2Adapter(protocol_version="http/1.1")

    # Call init_poolmanager
    with patch("requests_enhanced.adapters.PoolManager") as mock_pool_manager:
        adapter.init_poolmanager(10, 10, block=False)

        # Verify poolmanager was created with the standard method
        mock_pool_manager.assert_called_once()

        # Check that ssl_version was set
        call_kwargs = mock_pool_manager.call_args[1]
        assert call_kwargs.get("ssl_version") == "TLSv1.2"


def test_http2_adapter_init_poolmanager_with_exception():
    """Test HTTP2Adapter init_poolmanager handling exceptions."""
    # Create an adapter with HTTP/2 protocol
    adapter = HTTP2Adapter(protocol_version="h2")

    # Create a mock for PoolManager
    pool_manager_mock = MagicMock()

    # Set up the side effect for the first call
    def pool_manager_side_effect(*args, **kwargs):
        if not hasattr(pool_manager_side_effect, "called"):
            pool_manager_side_effect.called = True
            raise Exception("Custom poolmanager error")
        return pool_manager_mock

    # Patch PoolManager to use our mock with side effect
    with patch(
        "requests_enhanced.adapters.PoolManager", side_effect=pool_manager_side_effect
    ):
        # Call init_poolmanager - should handle the error and fall back
        adapter.init_poolmanager(10, 10, block=False)

        # Verify the adapter has a poolmanager attribute
        assert hasattr(adapter, "poolmanager")


def test_http2_adapter_init_poolmanager_alpn_type_error():
    """Test HTTP2Adapter init_poolmanager handling TypeError with alpn_protocols."""
    # Create an adapter with HTTP/1.1 protocol
    adapter = HTTP2Adapter(protocol_version="http/1.1")

    # Create a mock for PoolManager
    pool_manager_mock = MagicMock()

    # Set up the side effect for the first call
    def pool_manager_side_effect(*args, **kwargs):
        if not hasattr(pool_manager_side_effect, "called"):
            pool_manager_side_effect.called = True
            # Check if alpn_protocols is in kwargs
            if "alpn_protocols" in kwargs:
                raise TypeError("alpn_protocols is not a valid argument")
        return pool_manager_mock

    # Patch PoolManager to use our mock with side effect
    with patch(
        "requests_enhanced.adapters.PoolManager", side_effect=pool_manager_side_effect
    ):
        # Add alpn_protocols to test removal
        adapter.init_poolmanager(10, 10, block=False, alpn_protocols=["h2", "http/1.1"])

        # Verify the adapter has a poolmanager attribute
        assert hasattr(adapter, "poolmanager")


def test_http2_adapter_init_poolmanager_other_type_error():
    """Test HTTP2Adapter init_poolmanager handling other TypeError."""
    # Create an adapter with HTTP/1.1 protocol
    adapter = HTTP2Adapter(protocol_version="http/1.1")

    # Mock a TypeError not related to alpn_protocols
    with patch("requests_enhanced.adapters.PoolManager") as mock_pool_manager:
        # TypeError not mentioning alpn_protocols
        mock_pool_manager.side_effect = TypeError("Some other type error")

        # Should re-raise the error
        with pytest.raises(TypeError, match="Some other type error"):
            adapter.init_poolmanager(10, 10, block=False)


def test_http2_pool_manager_init():
    """Test HTTP2PoolManager initialization."""
    # Create an adapter with HTTP/2 protocol
    adapter = HTTP2Adapter(protocol_version="h2")

    # Call init_poolmanager to create the poolmanager
    adapter.init_poolmanager(10, 10, block=False)

    # Verify the poolmanager was created
    assert hasattr(adapter, "poolmanager")

    # Access the HTTP2PoolManager class through the adapter's poolmanager
    # This is a bit of a hack, but it's a way to test the inner class
    assert hasattr(adapter.poolmanager, "protocol")


def test_http2_pool_manager_new_pool_http():
    """Test HTTP2PoolManager _new_pool with HTTP scheme."""
    # First create the adapter and init the poolmanager
    adapter = HTTP2Adapter(protocol_version="h2")
    adapter.init_poolmanager(10, 10, block=False)

    # Get the poolmanager
    pool_manager = adapter.poolmanager

    # Mock the HTTPConnectionPool
    with patch("requests_enhanced.adapters.HTTPConnectionPool") as mock_http_pool:
        # Call _new_pool with HTTP scheme
        pool_manager._new_pool("http", "example.com", 80)

        # Verify HTTPConnectionPool was called
        mock_http_pool.assert_called_once()


def test_http2_pool_manager_new_pool_https():
    """Test HTTP2PoolManager _new_pool with HTTPS scheme."""
    # First create the adapter and init the poolmanager
    adapter = HTTP2Adapter(protocol_version="h2")
    adapter.init_poolmanager(10, 10, block=False)

    # Get the poolmanager
    pool_manager = adapter.poolmanager

    # Mock HTTP2ConnectionPool
    with patch("requests_enhanced.adapters.HTTP2ConnectionPool") as mock_http2_pool:
        # Call _new_pool with HTTPS scheme
        pool_manager._new_pool("https", "example.com", 443)

        # Verify HTTP2ConnectionPool was called
        mock_http2_pool.assert_called_once()


def test_http2_pool_manager_new_pool_type_error():
    """Test HTTP2PoolManager _new_pool handling TypeError."""
    # First create the adapter and init the poolmanager
    adapter = HTTP2Adapter(protocol_version="h2")
    adapter.init_poolmanager(10, 10, block=False)

    # Get the poolmanager
    pool_manager = adapter.poolmanager

    # Mock HTTP2ConnectionPool to raise TypeError
    with patch("requests_enhanced.adapters.HTTP2ConnectionPool") as mock_http2_pool:
        mock_http2_pool.side_effect = TypeError("Connection pool error")

        # Mock the standard pool classes for fallback
        with patch("requests_enhanced.adapters.HTTPSConnectionPool") as mock_https_pool:
            # Call _new_pool with HTTPS scheme - should fall back
            pool_manager._new_pool("https", "example.com", 443)

            # Verify HTTP2ConnectionPool was called and then fallback
            mock_http2_pool.assert_called_once()
            mock_https_pool.assert_called_once()
