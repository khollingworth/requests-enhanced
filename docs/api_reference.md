# API Reference

This document provides detailed information about the `requests-plus` API, including classes, methods, and exceptions.

## Core Components

### Session

```python
from requests_plus import Session
```

#### Constructor

```python
Session(
    retry_config: Optional[Retry] = None,
    timeout: Union[float, Tuple[float, float]] = (3.05, 30),
    max_retries: int = 3
)
```

**Parameters:**

- `retry_config`: Custom `requests.adapters.Retry` configuration. If `None`, a default will be created.
- `timeout`: Default timeout as `(connect_timeout, read_timeout)` tuple or single float.
- `max_retries`: Number of retries for requests (used only if `retry_config` is `None`).

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
session = Session(timeout=(5, 30), max_retries=5)
response = session.get("https://api.example.com/resources")
```

### Utility Functions

```python
from requests_plus.utils import json_get, json_post
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
from requests_plus.logging import configure_logger
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
from requests_plus.logging import configure_logger

logger = logging.getLogger("requests_plus")
configure_logger(logger, level=logging.DEBUG)
```

## Exceptions

### RequestsPlusError

Base exception for all `requests-plus` errors.

### RequestRetryError

Raised when max retries are exceeded.

```python
from requests_plus.exceptions import RequestRetryError

try:
    # Make a request
except RequestRetryError as e:
    print(f"Retry failed: {e}")
    print(f"Original exception: {e.original_exception}")
```

### RequestTimeoutError

Raised when a request times out.

```python
from requests_plus.exceptions import RequestTimeoutError

try:
    # Make a request
except RequestTimeoutError as e:
    print(f"Request timed out: {e}")
    print(f"Original exception: {e.original_exception}")
```

### MaxRetriesExceededError

Raised when the maximum number of retries is exceeded.