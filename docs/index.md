# requests-enhanced

> HTTP for Humans™, Now with OAuth, HTTP/2, and HTTP/3

Welcome to the official documentation for `requests-enhanced`, a powerful extension to the popular `requests` library that brings OAuth authentication, HTTP/2, and HTTP/3 support with intelligent protocol fallback mechanisms.

## Key Features

- **OAuth Authentication**: Full OAuth 1.0/1.1 and OAuth 2.0 support
- **Multi-Protocol Support**: HTTP/1.1, HTTP/2, and HTTP/3 in a single library
- **Intelligent Fallback**: Automatic degradation from HTTP/3 → HTTP/2 → HTTP/1.1
- **Enhanced Performance**: Connection pooling and persistent connections
- **Resilient Requests**: Advanced retry mechanisms with configurable backoff
- **Improved Error Handling**: Custom exceptions with detailed context
- **Modern Timeouts**: Fine-grained timeout controls
- **Comprehensive Logging**: Detailed request and connection logging

## Documentation

| Guide | Description |
|-------|-------------|
| [Tutorial](tutorial.md) | Comprehensive walkthrough for new users |
| [Usage Guide](usage_guide.md) | From basic to advanced usage patterns |
| [OAuth Usage Guide](oauth-usage-guide.md) | Complete guide to OAuth authentication |
| [Quick Reference](quick-reference.md) | Concise code snippets for common tasks |
| [API Reference](api_reference.md) | Detailed API documentation |

## Quick Installation

```bash
# Basic installation
pip install requests-enhanced

# With HTTP/2 support
pip install requests-enhanced[http2]

# With HTTP/3 support
pip install requests-enhanced[http3]

# With OAuth support
pip install requests-enhanced[oauth]

# Full installation with all features
pip install requests-enhanced[all]
```

## Basic Example

```python
from requests_enhanced import Session

# Create a session with HTTP/3 support (falls back to HTTP/2 and HTTP/1.1)
session = Session(http_version=3)

# Make a request - protocol negotiation happens automatically
response = session.get('https://example.com')
print(f"Response received with status: {response.status_code}")
print(f"Protocol used: {response.raw.version}")
```

## Project Links

- [GitHub Repository](https://github.com/kevinhollingworth/requests-plus)
- [PyPI Package](https://pypi.org/project/requests-enhanced/)
- [Issue Tracker](https://github.com/kevinhollingworth/requests-plus/issues)

## License

`requests-enhanced` is released under the MIT License. See the LICENSE file for details.