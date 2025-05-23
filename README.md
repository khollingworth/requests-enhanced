# Requests Enhanced

[![CI](https://github.com/khollingworth/requests-enhanced/actions/workflows/ci.yml/badge.svg)](https://github.com/khollingworth/requests-enhanced/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/requests-enhanced.svg?v=1.0.1&style=flat)](https://pypi.org/project/requests-enhanced/)
[![Python Versions](https://img.shields.io/pypi/pyversions/requests-enhanced.svg)](https://pypi.org/project/requests-enhanced/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

An enhanced wrapper for the popular `requests` library with advanced features for performance, authentication, and reliability in Python HTTP requests.

## Features

- **OAuth Authentication**: Full OAuth 1.0/1.1 and OAuth 2.0 support
  - Compatible with Twitter, GitHub, Google, Facebook and other OAuth providers
  - Thread-safe token management with automatic refresh
  - Seamless integration with HTTP/2 and HTTP/3

- **Modern Protocol Support**:
  - **HTTP/2**: Up to 40% faster than HTTP/1.1 for multiple requests
  - **HTTP/3**: QUIC protocol support with reduced latency
  - **Automatic Fallback**: Gracefully degrades HTTP/3 → HTTP/2 → HTTP/1.1

- **Reliability & Performance**:
  - **Configurable Retries**: Built-in retry mechanism with exponential backoff
  - **Enhanced Timeouts**: Fine-grained connect and read timeout control
  - **Improved Logging**: Detailed request and connection tracking
  - **Utility Functions**: Simplified JSON API operations

## Installation

```bash
# Basic installation from PyPI
pip install requests-enhanced

# With HTTP/2 support
pip install requests-enhanced[http2]

# With HTTP/3 support
pip install requests-enhanced[http3]

# With OAuth support
pip install requests-enhanced[oauth]

# With all features
pip install requests-enhanced[all]  # Includes HTTP/2, HTTP/3, and OAuth

# For development
git clone https://github.com/khollingworth/requests-enhanced.git
cd requests-enhanced
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from requests_enhanced import Session

# Create a session with default retry and timeout settings
session = Session()

# Use HTTP/2 protocol
http2_session = Session(http_version="2")

# Use HTTP/3 with automatic fallback
http3_session = Session(http_version="3")

# Simple GET request
response = session.get("https://api.example.com/resources")
print(response.json())
```

## Documentation

- **[Tutorial](docs/tutorial.md)**: Comprehensive guide covering all features
- **[Quick Reference](docs/quick-reference.md)**: Concise cheat sheet for common patterns
- **[OAuth Usage Guide](docs/oauth-usage-guide.md)**: Complete guide for OAuth 1.0/1.1 and OAuth 2.0
- **[Examples](examples/)**: Real-world code examples including:
  - [Basic Usage](examples/basic_usage.py)
  - [API Integration](examples/api_integration_example.py)
  - [Advanced Sessions](examples/advanced_session_example.py)
  - [HTTP/2 Example](examples/http2_example.py)
  - [HTTP/3 Example](examples/http3_example.py)
  - [OAuth Examples](examples/oauth_example.py)
  - [Retry Patterns](examples/retry_example.py)

## HTTP/2 Support

The library provides robust HTTP/2 support with significant performance improvements:

### Performance Benefits

- **30-40% faster** for multiple concurrent requests to the same host
- **Multiplexed connections**: Multiple requests share a single connection
- **Header compression**: Reduces overhead and improves load times
- **Binary framing**: More efficient data transfer
- **Server push**: Allows servers to preemptively send resources
- **Automatic fallback**: Gracefully falls back to HTTP/1.1 when needed

### Compatibility

- Works with urllib3 versions 1.x and 2.x
- Compatible with Python 3.7+
- Requires TLS 1.2 or higher

See the [HTTP/2 example](examples/http2_example.py) for a performance comparison and the [API Reference](docs/api_reference.md#http2-support) for configuration details.

### Using HTTP/2

Enabling HTTP/2 is simple:

```python
from requests_enhanced import Session, HTTP2_AVAILABLE

# Check if HTTP/2 support is available
if HTTP2_AVAILABLE:
    print("HTTP/2 support is enabled")
else:
    print("HTTP/2 dependencies not installed, install with: pip install requests-enhanced[http2]")

# Create a session with HTTP/2 support
session = Session(http_version="2")

# Make requests as usual - HTTP/2 will be used automatically for HTTPS connections
response = session.get("https://api.example.com/resources")

# HTTP/1.1 will still be used for HTTP connections or if server doesn't support HTTP/2
```

### Manual Configuration

For advanced use cases, you can manually configure the HTTP/2 adapter:

```python
from requests_enhanced import Session, HTTP2Adapter

session = Session()

# Mount HTTP/2 adapter for HTTPS URLs
http2_adapter = HTTP2Adapter()
session.mount("https://", http2_adapter)

# Keep standard adapter for HTTP URLs
from requests.adapters import HTTPAdapter
session.mount("http://", HTTPAdapter())
```

# POST request with JSON data
```python
data = {"name": "example", "value": 42}
response = session.post("https://api.example.com/resources", json=data)
```

## Utility Functions

For quick, one-off requests:

```python
from requests_enhanced.utils import json_get, json_post

# GET request that automatically returns JSON
data = json_get("https://api.example.com/resources")

# POST request with automatic JSON handling
result = json_post("https://api.example.com/resources", data={"name": "example"})
```

### OAuth Authentication

```python
from requests_enhanced import OAuth1EnhancedSession, OAuth2EnhancedSession

# OAuth 1.0/1.1 example (Twitter-style)
oauth1_session = OAuth1EnhancedSession(
    client_key="your_consumer_key",
    client_secret="your_consumer_secret",
    resource_owner_key="user_token",
    resource_owner_secret="user_secret",
    http_version="2"  # Use HTTP/2
)
response = oauth1_session.get("https://api.twitter.com/1.1/account/verify_credentials.json")

# OAuth 2.0 example (GitHub-style)
oauth2_session = OAuth2EnhancedSession(
    client_id="your_client_id",
    http_version="3"  # Use HTTP/3 with automatic fallback
)

# Generate authorization URL for user to visit
auth_url, state = oauth2_session.authorization_url(
    "https://github.com/login/oauth/authorize",
    scope=["user", "repo"]
)

# After user authorization, exchange code for token
token = oauth2_session.fetch_token(
    "https://github.com/login/oauth/access_token",
    client_secret="your_client_secret",
    authorization_response="https://example.com/callback?code=auth_code"
)

# Make authenticated requests
response = oauth2_session.get("https://api.github.com/user")
```

## Error Handling

```python
from requests_enhanced import Session
from requests_enhanced.exceptions import RequestTimeoutError, RequestRetryError

try:
    session = Session()
    response = session.get("https://api.example.com/resources")
except RequestTimeoutError as e:
    print(f"Request timed out: {e}")
    print(f"Original exception: {e.original_exception}")
except RequestRetryError as e:
    print(f"Retry failed: {e}")
```

## Documentation

Detailed documentation is available in the [docs](docs/) directory:

- [Quickstart Guide](docs/quickstart.md): Get up and running quickly
- [Usage Guide](docs/usage.md): Detailed usage examples and patterns
- [API Reference](docs/api_reference.md): Complete API documentation

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/khollingworth/requests-enhanced.git
cd requests-enhanced

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/requests_enhanced --cov-report=term-missing

# Run specific test file
pytest tests/test_sessions.py
```

### Code Style

This project uses black for code formatting and flake8 for linting:

```bash
# Format code
black src tests examples

# Check code style
flake8 src tests examples
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.