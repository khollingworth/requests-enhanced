"""
Tests for adapter compatibility with different urllib3 versions.
"""

import pytest
from unittest.mock import patch, Mock

# Conditionally import the HTTP/2 adapter
try:
    from requests_enhanced.adapters import HTTP2Adapter, HTTP2_AVAILABLE
except ImportError:
    # Set fallback values if module cannot be imported
    # Use type ignore comments to bypass mypy errors in test files
    HTTP2Adapter = None  # type: ignore
    HTTP2_AVAILABLE = False

# Skip all tests in this module if HTTP/2 is not available
pytestmark = pytest.mark.skipif(
    not HTTP2_AVAILABLE,
    reason="HTTP/2 dependencies not available (h2, hyperframe, hpack)",
)


@pytest.fixture
def urllib3_v1():
    """Fixture to simulate urllib3 v1.x environment."""
    with patch("requests_enhanced.adapters.URLLIB3_VERSION", "1.26.16"):
        with patch("requests_enhanced.adapters.URLLIB3_MAJOR", 1):
            with patch("requests_enhanced.adapters.HTTP2_AVAILABLE", True):
                yield


@pytest.fixture
def urllib3_v2():
    """Fixture to simulate urllib3 v2.x environment."""
    with patch("requests_enhanced.adapters.URLLIB3_VERSION", "2.0.3"):
        with patch("requests_enhanced.adapters.URLLIB3_MAJOR", 2):
            with patch("requests_enhanced.adapters.HTTP2_AVAILABLE", True):
                yield


def test_adapter_init_with_urllib3_v1(urllib3_v1):
    """Test adapter initialization with urllib3 v1.x."""
    # When HTTP2_AVAILABLE is patched to True in the fixture,
    # and we don't specify a protocol_version, the adapter defaults to "h2"
    adapter = HTTP2Adapter()
    assert adapter is not None

    # Explicitly set HTTP/1.1 to test that case
    adapter = HTTP2Adapter(protocol_version="http/1.1")
    assert adapter.protocol_version == "http/1.1"


def test_adapter_init_with_urllib3_v2(urllib3_v2):
    """Test adapter initialization with urllib3 v2.x."""
    # When HTTP2_AVAILABLE is patched to True in the fixture,
    # and we don't specify a protocol_version, the adapter defaults to "h2"
    adapter = HTTP2Adapter()
    assert adapter is not None

    # Explicitly set HTTP/1.1 to test that case
    adapter = HTTP2Adapter(protocol_version="http/1.1")
    assert adapter.protocol_version == "http/1.1"


def test_http2_adapter_poolmanager_with_urllib3_v1(urllib3_v1):
    """Test HTTP/2 pool manager initialization with urllib3 v1.x."""
    adapter = HTTP2Adapter(protocol_version="h2")

    # Initialize the pool manager
    adapter.init_poolmanager(1, 1, block=False)

    # Check that a pool manager was created
    assert adapter.poolmanager is not None
    assert adapter.protocol_version == "h2"


def test_http2_adapter_poolmanager_with_urllib3_v2(urllib3_v2):
    """Test HTTP/2 pool manager initialization with urllib3 v2.x."""
    adapter = HTTP2Adapter(protocol_version="h2")

    # Initialize the pool manager
    adapter.init_poolmanager(1, 1, block=False)

    # Check that a pool manager was created
    assert adapter.poolmanager is not None
    assert adapter.protocol_version == "h2"


def test_adapter_send_common_methods():
    """Test adapter common methods with different urllib3 versions."""
    versions = [("1.26.16", 1), ("2.0.3", 2)]

    for version, major in versions:
        with patch("requests_enhanced.adapters.URLLIB3_VERSION", version):
            with patch("requests_enhanced.adapters.URLLIB3_MAJOR", major):
                with patch("requests_enhanced.adapters.HTTP2_AVAILABLE", True):
                    adapter = HTTP2Adapter(protocol_version="h2")

                    # Create a request to test various methods
                    request = Mock()
                    request.url = "https://example.com"
                    request.method = "GET"
                    request.headers = {}

                    # Test add_headers (this method is inherited from HTTPAdapter)
                    adapter.add_headers(request)

                    # Initialize the pool manager
                    adapter.init_poolmanager(1, 1, block=False)
                    assert adapter.poolmanager is not None


def test_adapter_protocol_detection():
    """Test adapter protocol detection with different urllib3 versions."""
    versions = [("1.26.16", 1), ("2.0.3", 2)]

    for version, major in versions:
        with patch("requests_enhanced.adapters.URLLIB3_VERSION", version):
            with patch("requests_enhanced.adapters.URLLIB3_MAJOR", major):
                # Test with HTTP2_AVAILABLE = False
                with patch("requests_enhanced.adapters.HTTP2_AVAILABLE", False):
                    # Default constructor with http/1.1 should work
                    adapter = HTTP2Adapter(protocol_version="http/1.1")
                    assert adapter.protocol_version == "http/1.1"

                    # Using h2 with dependencies not available should raise ImportError
                    with pytest.raises(ImportError):
                        HTTP2Adapter(protocol_version="h2")

                # Test with HTTP2_AVAILABLE = True
                with patch("requests_enhanced.adapters.HTTP2_AVAILABLE", True):
                    # When explicitly set to HTTP/1.1
                    adapter = HTTP2Adapter(protocol_version="http/1.1")
                    assert adapter.protocol_version == "http/1.1"

                    # When explicitly set to HTTP/2
                    adapter = HTTP2Adapter(protocol_version="h2")
                    assert adapter.protocol_version == "h2"
