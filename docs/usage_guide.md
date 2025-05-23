# Usage Guide for requests-enhanced

This comprehensive guide will help you get started with the Requests Enhanced library and explore its advanced features.

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Utility Functions](#utility-functions)
4. [Advanced Features](#advanced-features)
   - [Configuring Retries](#configuring-retries)
   - [Timeout Configuration](#timeout-configuration)
   - [HTTP/2 and HTTP/3 Support](#http2-and-http3-support)
   - [Session Management](#session-management)

## Installation

```bash
# Basic installation
pip install requests-enhanced

# With HTTP/2 support
pip install requests-enhanced[http2]

# With HTTP/3 support
pip install requests-enhanced[http3]

# With all features
pip install requests-enhanced[all]
```

## Basic Usage

```python
from requests_enhanced import Session

# Create a session with default retry and timeout settings
session = Session()

# Simple GET request
response = session.get("https://api.example.com/resources")
print(response.json())

# POST request with JSON data
data = {"name": "example", "value": 42}
response = session.post("https://api.example.com/resources", json=data)
print(response.status_code)
```

## Utility Functions

```python
from requests_enhanced.utils import json_get, json_post

# GET request that automatically returns JSON
data = json_get("https://api.example.com/resources")

# POST request with automatic JSON handling
result = json_post("https://api.example.com/resources", data={"name": "example"})
```

## Advanced Features

### Configuring Retries

```python
from requests_enhanced import Session
from requests.adapters import Retry

# Custom retry configuration
retry_config = Retry(
    total=5,  # Total number of retries
    backoff_factor=0.5,  # Backoff factor between retries
    status_forcelist=[500, 502, 503, 504],  # Status codes to retry on
    allowed_methods=["GET", "POST"]  # HTTP methods to retry
)

# Create session with custom retry configuration
session = Session(retry_config=retry_config)
response = session.get("https://api.example.com/resources")
```

### Timeout Configuration

```python
from requests_enhanced import Session

# Set custom timeout (connect_timeout, read_timeout)
session = Session(timeout=(3.05, 27))

# Timeout will be applied to all requests
response = session.get("https://api.example.com/resources")

# Override timeout for a specific request
response = session.get("https://api.example.com/slow-resource", timeout=(5, 60))
```

### Error Handling

```python
from requests_enhanced import Session
from requests_enhanced.exceptions import RequestTimeoutError, RequestRetryError

try:
    session = Session()
    response = session.get("https://api.example.com/resources")
    data = response.json()
except RequestTimeoutError as e:
    print(f"Request timed out: {e}")
    print(f"Original exception: {e.original_exception}")
except RequestRetryError as e:
    print(f"Retry failed: {e}")
    print(f"Original exception: {e.original_exception}")
```

### Custom Logging

```python
import logging
from requests_enhanced.logging import configure_logger

# Get the requests_enhanced logger
logger = logging.getLogger("requests_enhanced")

# Configure with custom format and level
configure_logger(logger, level=logging.DEBUG, log_format="%(asctime)s - %(levelname)s - %(message)s")
```

### HTTP/2 and HTTP/3 Support

```python
from requests_enhanced import Session
from requests_enhanced.adapters import HTTP2Adapter, HTTP3Adapter

# Create a session with HTTP/2 support
session = Session(http_version=2)
response = session.get("https://http2.example.com")

# Or explicitly mount HTTP/2 adapter
session = Session()
session.mount("https://", HTTP2Adapter())
response = session.get("https://http2.example.com")

# Using HTTP/3 with automatic fallback to HTTP/2 and HTTP/1.1
session = Session(http_version=3)
response = session.get("https://http3.example.com")
```

### Session Management

```python
from requests_enhanced import Session

# Using context manager for automatic cleanup
with Session() as session:
    response = session.get("https://api.example.com/resources")
    # Session will be automatically closed when exiting the with block

# Reusing a session for multiple requests (connection pooling)
session = Session()
for i in range(10):
    response = session.get(f"https://api.example.com/resources/{i}")
    # Uses the same connection pool for better performance
session.close()  # Explicitly close when done