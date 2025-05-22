# Detailed Usage Guide

This guide covers advanced usage patterns for the Requests Enhanced library.

## Configuring Retries

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

## Timeout Configuration

```python
from requests_enhanced import Session

# Set custom timeout (connect_timeout, read_timeout)
session = Session(timeout=(3.05, 27))

# Timeout will be applied to all requests
response = session.get("https://api.example.com/resources")

# Override timeout for a specific request
response = session.get("https://api.example.com/slow-resource", timeout=(5, 60))
```

## Error Handling

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

## Custom Logging

```python
import logging
from requests_enhanced.logging import configure_logger

# Get the requests_enhanced logger
logger = logging.getLogger("requests_enhanced")

# Configure with custom format and level
configure_logger(logger, level=logging.DEBUG, log_format="%(asctime)s - %(levelname)s - %(message)s")
```