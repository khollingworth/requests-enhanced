# API Reference

This document provides detailed information about the `requests-enhanced` API, including classes, methods, and exceptions.

## Core Components

### Session

```python
from requests_enhanced import Session
```

#### Constructor

```python
Session(
    retry_config: Optional[Retry] = None,
    timeout: Union[float, Tuple[float, float]] = (3.05, 30),
    max_retries: int = 3,
    http_version: Literal["1.1", "2", "3"] = "1.1"
)
```

**Parameters:**

- `retry_config`: Custom `requests.adapters.Retry` configuration. If `None`, a default will be created.
- `timeout`: Default timeout as `(connect_timeout, read_timeout)` tuple or single float.
- `max_retries`: Number of retries for requests (used only if `retry_config` is `None`).
- `http_version`: HTTP protocol version to use. Options:
  - `"1.1"`: Standard HTTP/1.1 (default)
  - `"2"`: HTTP/2 for improved performance
  - `"3"`: HTTP/3 for maximum performance with automatic fallback to HTTP/2 and HTTP/1.1 if not available

#### Methods

The `Session` class inherits all methods from `requests.Session`, with enhanced error handling:

- `get(url, **kwargs)`: Send a GET request
- `post(url, **kwargs)`: Send a POST request
- `put(url, **kwargs)`: Send a PUT request
- `delete(url, **kwargs)`: Send a DELETE request
- `head(url, **kwargs)`: Send a HEAD request
- `options(url, **kwargs)`: Send an OPTIONS request
- `patch(url, **kwargs)`: Send a PATCH request

All methods accept the same parameters as the corresponding `requests.Session` methods, with the addition of:

- `timeout`: Optional timeout override for this specific request

#### Example

```python
# Standard session with HTTP/1.1
session = Session(timeout=(5, 30), max_retries=5)
response = session.get("https://api.example.com/resources")

# HTTP/2 enabled session for improved performance
session_http2 = Session(timeout=(5, 30), max_retries=5, http_version="2")
response = session_http2.get("https://api.example.com/resources")

# HTTP/3 enabled session with automatic fallback to HTTP/2 and HTTP/1.1
session_http3 = Session(timeout=(5, 30), max_retries=5, http_version="3")
response = session_http3.get("https://api.example.com/resources")
```

### HTTP/2 Support

```python
from requests_enhanced import HTTP2Adapter, HTTP2_AVAILABLE
```

The library provides HTTP/2 protocol support through the `HTTP2Adapter` class and the `HTTP2_AVAILABLE` flag.

#### HTTP2_AVAILABLE

A boolean flag indicating whether HTTP/2 dependencies are installed and available.

```python
if HTTP2_AVAILABLE:
    print("HTTP/2 support is available")
else:
    print("HTTP/2 dependencies not installed. Install with: pip install requests-enhanced[http2]")
```

#### HTTP2Adapter

```python
HTTP2Adapter(
    pool_connections: int = 10,
    pool_maxsize: int = 10,
    max_retries: Union[Retry, int, None] = None,
    pool_block: bool = False,
    protocol_version: str = "h2"
)
```

**Parameters:**

- `pool_connections`: Number of connection pools to cache
- `pool_maxsize`: Maximum number of connections to save in the pool
- `max_retries`: Retry configuration to use
- `pool_block`: Whether the connection pool should block for connections
- `protocol_version`: HTTP protocol version to use ("h2" for HTTP/2, "http/1.1" for HTTP/1.1)

**Example:**

```python
# HTTP/2 Support

`requests-enhanced` provides robust HTTP/2 support with automatic fallback to HTTP/1.1 when needed. HTTP/2 offers significant performance improvements through connection multiplexing, header compression, and binary framing.

## Performance Benefits

HTTP/2 typically provides the following advantages over HTTP/1.1:

- **Connection Multiplexing**: Multiple requests can share a single connection
- **Header Compression**: Reduces overhead by compressing HTTP headers
- **Binary Protocol**: More efficient than HTTP/1.1's text-based protocol
- **Server Push**: Servers can proactively send resources before they're requested
- **Stream Prioritization**: Critical resources can be delivered first

Our benchmarks show HTTP/2 performing **30-40% faster** for multiple concurrent requests to the same host.

## Basic Usage

The simplest way to enable HTTP/2 is to specify it when creating a `Session`:

```python
from requests_enhanced import Session

# Create a session with HTTP/2 enabled
session = Session(http_version="2")

# Make requests as usual - HTTP/2 will be used when supported by the server
response = session.get("https://example.com")
```

## Dependency Management

HTTP/2 support requires additional dependencies. Install them with:

```bash
pip install requests-enhanced[http2]
```

Or manually install the required packages:

```bash
pip install h2 hyperframe hpack
```

## Automatic Fallback

The library is designed to gracefully fall back to HTTP/1.1 in these scenarios:

- When HTTP/2 dependencies are not installed
- When a server doesn't support HTTP/2
- When protocol negotiation fails
- When connection errors occur with HTTP/2

This ensures your application continues to work even when HTTP/2 isn't available.

## Compatibility

The HTTP/2 implementation is compatible with:

- urllib3 versions 1.x and 2.x
- Python 3.7 and newer
- TLS 1.2 or higher (required for HTTP/2)

## Manual Configuration

For more control, you can manually configure the HTTP/2 adapter:

```python
from requests_enhanced import HTTP2Adapter, Session

session = Session()

# Only mount for HTTPS as HTTP/2 requires TLS
http2_adapter = HTTP2Adapter(protocol_version="h2")
session.mount("https://", http2_adapter)

# Use standard adapter for HTTP connections
from requests.adapters import HTTPAdapter
session.mount("http://", HTTPAdapter())
```

## Dependency Management

HTTP/2 support requires additional dependencies. You can install them with:

```bash
pip install requests-enhanced[http2]
```

Or manually install the required package:

```bash
pip install h2
```

## Automatic Fallback

If HTTP/2 dependencies are not available or if the server doesn't support HTTP/2, the library will automatically fall back to HTTP/1.1:

```python
from requests_enhanced import Session, HTTP2_AVAILABLE

# Check if HTTP/2 is available
print(f"HTTP/2 support available: {HTTP2_AVAILABLE}")

# Create session with HTTP/2 requested
session = Session(http_version="2")

# If HTTP/2 dependencies are not available, this will use HTTP/1.1
response = session.get("https://example.com")
```

## Performance Benefits

HTTP/2 provides significant performance improvements, especially for multiple requests to the same domain:

- **Multiplexing**: Multiple requests over a single connection
- **Header Compression**: Reduced overhead for repeated headers
- **Server Push**: Preemptive sending of resources
- **Binary Protocol**: More efficient parsing

> **Note:** For most use cases, it's simpler to use `Session(http_version="2")` which automatically configures the appropriate adapters.

### HTTP/3 Support

```python
from requests_enhanced import HTTP3Adapter, HTTP3_AVAILABLE
```

The library provides HTTP/3 protocol support through the `HTTP3Adapter` class and the `HTTP3_AVAILABLE` flag. HTTP/3 uses QUIC (Quick UDP Internet Connections) transport protocol which can provide reduced latency and better performance, especially on high-latency or lossy connections.

#### HTTP3_AVAILABLE

A boolean flag indicating whether HTTP/3 dependencies are installed and available.

```python
if HTTP3_AVAILABLE:
    print("HTTP/3 support is available")
else:
    print("HTTP/3 dependencies not installed. Install with: pip install requests-enhanced[http3]")
```

#### HTTP3Adapter

```python
HTTP3Adapter(
    pool_connections: int = 10,
    pool_maxsize: int = 10,
    max_retries: Union[Retry, int, None] = None,
    pool_block: bool = False
)
```

**Parameters:**

- `pool_connections`: Number of connection pools to cache
- `pool_maxsize`: Maximum number of connections to save in the pool
- `max_retries`: Retry configuration to use
- `pool_block`: Whether the connection pool should block for connections

**Example:**

```python
# HTTP/3 Support with automatic fallback
from requests_enhanced import Session, HTTP3Adapter, HTTP3_AVAILABLE

# Check if HTTP/3 is available
print(f"HTTP/3 support available: {HTTP3_AVAILABLE}")

# Mount HTTP/3 adapter (with automatic fallback)
session = Session()
http3_adapter = HTTP3Adapter()
session.mount("https://", http3_adapter)

# Will use HTTP/3 if available, falling back to HTTP/2 and HTTP/1.1 if not
response = session.get("https://example.com")
```

#### Automatic Fallback Mechanism

The HTTP/3 adapter includes a robust fallback mechanism:

1. First attempts to connect using HTTP/3 (QUIC)
2. If HTTP/3 fails, falls back to HTTP/2
3. If HTTP/2 fails, falls back to HTTP/1.1

This ensures maximum compatibility while allowing your application to take advantage of the latest protocols when available.

**Example with Session:**

```python
# Simplest way to use HTTP/3 with automatic fallback
session = Session(http_version="3")
response = session.get("https://example.com")

# The protocol version used is available in the response
print(f"Protocol used: {response.raw.version}")
```

#### Dependency Management

HTTP/3 support requires additional dependencies. You can install them with:

```bash
pip install requests-enhanced[http3]
```

Or manually install the required packages:

```bash
pip install aioquic
```

> **Note:** For most use cases, it's simpler to use `Session(http_version="3")` which automatically configures the appropriate adapters and handles fallback logic.

### Utility Functions

```python
from requests_enhanced.utils import json_get, json_post
```

#### json_get

```python
json_get(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    **kwargs: Any
) -> Dict[str, Any]
```

Make a GET request and return the JSON response.

**Parameters:**

- `url`: The URL to request
- `params`: Optional query parameters
- `**kwargs`: Additional arguments to pass to the request

**Returns:**

- Parsed JSON response as a dictionary

**Raises:**

- `RequestTimeoutError`: When the request times out
- `RequestRetryError`: When max retries are exceeded
- `ValueError`: When the response is not valid JSON

#### json_post

```python
json_post(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    **kwargs: Any
) -> Dict[str, Any]
```

Make a POST request with JSON data and return the JSON response.

**Parameters:**

- `url`: The URL to request
- `data`: Optional form data
- `json`: Optional JSON data
- `**kwargs`: Additional arguments to pass to the request

**Returns:**

- Parsed JSON response as a dictionary

**Raises:**

- `RequestTimeoutError`: When the request times out
- `RequestRetryError`: When max retries are exceeded
- `ValueError`: When the response is not valid JSON

### Logging Configuration

```python
from requests_enhanced.logging import configure_logger
```

#### configure_logger

```python
configure_logger(
    logger: logging.Logger,
    level: int = logging.INFO,
    handler: Optional[logging.Handler] = None,
    log_format: Optional[str] = None
) -> logging.Logger
```

Configure a logger with the specified level, handler, and format.

**Parameters:**

- `logger`: The logger to configure
- `level`: Logging level (e.g., `logging.INFO`, `logging.DEBUG`)
- `handler`: Optional handler to add to the logger. If `None`, a `StreamHandler` will be created.
- `log_format`: Format string for log messages. If `None` and handler has no formatter, `DEFAULT_LOG_FORMAT` will be used.

**Returns:**

- The configured logger

**Example:**

```python
import logging
from requests_enhanced.logging import configure_logger

logger = logging.getLogger("requests_enhanced")
configure_logger(logger, level=logging.DEBUG)
```

## Exceptions

### RequestsEnhancedError

Base exception for all `requests-enhanced` errors.

### RequestRetryError

Raised when max retries are exceeded.

```python
from requests_enhanced.exceptions import RequestRetryError

try:
    # Make a request
except RequestRetryError as e:
    print(f"Retry failed: {e}")
    print(f"Original exception: {e.original_exception}")
```

### RequestTimeoutError

Raised when a request times out.

```python
from requests_enhanced.exceptions import RequestTimeoutError

try:
    # Make a request
except RequestTimeoutError as e:
    print(f"Request timed out: {e}")
    print(f"Original exception: {e.original_exception}")
```

### MaxRetriesExceededError

Raised when the maximum number of retries is exceeded.