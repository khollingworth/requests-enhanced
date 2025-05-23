# requests-enhanced Tutorial

This tutorial will guide you through using `requests-enhanced`, a powerful HTTP library that extends the popular `requests` library with HTTP/2 and HTTP/3 support, enhanced retry mechanisms, and better connection management.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Basic Usage](#basic-usage)
4. [Advanced Features](#advanced-features)
5. [HTTP/2 and HTTP/3](#http2-and-http3)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)
8. [Migration from requests](#migration-from-requests)

## Installation

```bash
# Basic installation
pip install requests-enhanced

# With HTTP/2 support
pip install requests-enhanced[http2]

# With HTTP/3 support (experimental)
pip install requests-enhanced[http3]

# All features
pip install requests-enhanced[all]
```

## Quick Start

```python
from requests_enhanced import Session

# Create a session with automatic retries
session = Session(max_retries=3)

# Make a simple GET request
response = session.get('https://api.github.com')
print(response.json())
```

## Basic Usage

### Making Different Types of Requests

```python
from requests_enhanced import Session

session = Session()

# GET request
response = session.get('https://httpbin.org/get')

# POST request with JSON data
data = {'name': 'John', 'age': 30}
response = session.post('https://httpbin.org/post', json=data)

# PUT request
response = session.put('https://httpbin.org/put', json=data)

# DELETE request
response = session.delete('https://httpbin.org/delete')

# PATCH request
response = session.patch('https://httpbin.org/patch', json={'name': 'Jane'})
```

### Request Parameters

```python
# URL parameters
params = {'page': 2, 'per_page': 50}
response = session.get('https://api.example.com/users', params=params)

# Request headers
headers = {'Authorization': 'Bearer YOUR_TOKEN'}
response = session.get('https://api.example.com/profile', headers=headers)

# Request timeout
response = session.get('https://httpbin.org/delay/2', timeout=5)

# Form data
form_data = {'username': 'user', 'password': 'pass'}
response = session.post('https://httpbin.org/post', data=form_data)
```

### Working with Responses

```python
response = session.get('https://httpbin.org/get')

# Status code
print(response.status_code)  # 200

# Response headers
print(response.headers['Content-Type'])

# Response body as text
print(response.text)

# Response body as JSON
data = response.json()

# Response body as bytes
binary_data = response.content

# Check if request was successful
response.raise_for_status()  # Raises exception for 4xx/5xx status codes
```

## Advanced Features

### Enhanced Retry Mechanism

```python
from requests_enhanced import Session
from urllib3.util.retry import Retry

# Basic retry configuration
session = Session(
    max_retries=5,
    retry_backoff_factor=0.3,  # Wait 0.3s, 0.6s, 1.2s, etc. between retries
    retry_on=[500, 502, 503, 504]  # Retry on these status codes
)

# Custom retry strategy
custom_retry = Retry(
    total=10,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST", "PUT", "DELETE"],
    respect_retry_after_header=True
)

session = Session()
adapter = session.get_adapter("https://")
adapter.max_retries = custom_retry
```

### Connection Pooling

```python
# Configure connection pooling for better performance
session = Session(
    pool_connections=20,  # Number of connection pools to cache
    pool_maxsize=100,    # Maximum connections to save in the pool
)

# Make multiple requests to the same host
# Connections will be reused for better performance
for i in range(100):
    response = session.get(f'https://api.example.com/item/{i}')
```

### Session Persistence

```python
# Create a session with persistent configuration
session = Session(
    max_retries=3,
    timeout=30,
    headers={
        'User-Agent': 'MyApp/1.0',
        'Accept': 'application/json'
    }
)

# All requests will use these settings
response1 = session.get('https://api.example.com/endpoint1')
response2 = session.get('https://api.example.com/endpoint2')
```

## HTTP/2 and HTTP/3

### Using HTTP/2

```python
from requests_enhanced import Session, HTTP2Adapter

session = Session()

# Mount HTTP/2 adapter for specific domains
http2_adapter = HTTP2Adapter()
session.mount("https://http2-enabled-site.com", http2_adapter)

# Requests to this domain will use HTTP/2
response = session.get('https://http2-enabled-site.com/api/data')

# Check protocol version
print(f"Protocol: {response.raw.version}")  # Should show HTTP/2
```

### Using HTTP/3 (Experimental)

```python
from requests_enhanced import Session, HTTP3Adapter
from requests_enhanced.adapters import HTTP3_AVAILABLE

if HTTP3_AVAILABLE:
    session = Session()
    
    # Mount HTTP/3 adapter
    http3_adapter = HTTP3Adapter()
    session.mount("https://quic-enabled-site.com", http3_adapter)
    
    # Requests will use HTTP/3 with automatic fallback to HTTP/2
    response = session.get('https://quic-enabled-site.com/api/data')
else:
    print("HTTP/3 dependencies not installed")
```

### Protocol-Specific Benefits

**HTTP/2 Benefits:**
- Multiplexing: Multiple requests over a single connection
- Header compression: Reduced overhead
- Server push: Proactive resource sending
- Binary protocol: More efficient parsing

**HTTP/3 Benefits:**
- QUIC transport: Faster connection establishment
- Better performance on unreliable networks
- Reduced head-of-line blocking
- Connection migration support

## Error Handling

### Basic Error Handling

```python
from requests_enhanced import Session
from requests_enhanced.exceptions import (
    RequestException,
    RequestTimeoutError,
    RequestRetryError,
    HTTPError
)

session = Session(max_retries=3, timeout=10)

try:
    response = session.get('https://api.example.com/data')
    response.raise_for_status()  # Raise exception for bad status codes
    data = response.json()
except RequestTimeoutError:
    print("Request timed out")
except RequestRetryError as e:
    print(f"Failed after {session.max_retries} retries: {e}")
except HTTPError as e:
    print(f"HTTP error occurred: {e}")
except RequestException as e:
    print(f"Request failed: {e}")
```

### Handling Specific Status Codes

```python
response = session.get('https://api.example.com/resource')

if response.status_code == 200:
    print("Success!")
elif response.status_code == 404:
    print("Resource not found")
elif response.status_code == 429:
    # Rate limited - check for Retry-After header
    retry_after = response.headers.get('Retry-After', 60)
    print(f"Rate limited. Retry after {retry_after} seconds")
elif response.status_code >= 500:
    print("Server error")
```

## Best Practices

### 1. Always Use Sessions

```python
# Good - reuses connections
with Session() as session:
    for url in urls:
        response = session.get(url)

# Less efficient - creates new connection each time
import requests
for url in urls:
    response = requests.get(url)
```

### 2. Set Appropriate Timeouts

```python
# Always set timeouts to prevent hanging requests
session = Session(timeout=30)

# Or per-request timeout
response = session.get('https://api.example.com', timeout=(3.05, 27))
# (connection timeout, read timeout)
```

### 3. Handle Errors Gracefully

```python
def safe_api_call(session, url):
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except RequestTimeoutError:
        logging.error(f"Timeout accessing {url}")
        return None
    except RequestException as e:
        logging.error(f"Error accessing {url}: {e}")
        return None
```

### 4. Use Connection Pooling for Multiple Requests

```python
# Configure for your use case
session = Session(
    pool_connections=10,  # Adjust based on number of different hosts
    pool_maxsize=50,     # Adjust based on concurrent requests
)
```

### 5. Respect Rate Limits

```python
import time

def rate_limited_request(session, url, max_retries=3):
    for attempt in range(max_retries):
        response = session.get(url)
        
        if response.status_code == 429:
            # Rate limited
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            continue
            
        return response
    
    raise Exception("Max retries exceeded")
```

## Migration from requests

`requests-enhanced` is designed to be a drop-in replacement for `requests`. Here's how to migrate:

### Simple Migration

```python
# Before
import requests
response = requests.get('https://api.example.com')

# After
from requests_enhanced import Session
session = Session()
response = session.get('https://api.example.com')
```

### Using Global Functions

```python
# You can also use the familiar requests API
import requests_enhanced as requests

response = requests.get('https://api.example.com')
response = requests.post('https://api.example.com', json={'data': 'value'})
```

### Key Differences

1. **Better Defaults**: requests-enhanced includes retry logic by default
2. **HTTP/2 and HTTP/3**: Automatic protocol negotiation and fallback
3. **Enhanced Exceptions**: More specific error types for better error handling
4. **Connection Management**: Better connection pooling and reuse

### Compatibility Note

All existing `requests` code should work with `requests-enhanced`. The library extends functionality while maintaining backward compatibility.

## Next Steps

- Check out the [examples directory](../examples/) for more code samples
- Read the [API documentation](api.md) for detailed reference
- Explore [advanced features](advanced.md) for power users
- Join our [community](https://github.com/your-repo/discussions) for support

Happy coding with requests-enhanced! 🚀
