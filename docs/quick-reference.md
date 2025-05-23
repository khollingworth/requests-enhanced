# requests-enhanced Quick Reference

## Installation

```bash
pip install requests-enhanced              # Basic
pip install requests-enhanced[http2]       # With HTTP/2
pip install requests-enhanced[http3]       # With HTTP/3
pip install requests-enhanced[all]         # Everything
```

## Basic Usage

```python
from requests_enhanced import Session

# Create session
session = Session()

# Make requests
r = session.get('https://api.example.com')
r = session.post('https://api.example.com', json={'key': 'value'})
r = session.put('https://api.example.com', data='content')
r = session.delete('https://api.example.com/item/1')
r = session.patch('https://api.example.com', json={'update': 'value'})
```

## Session Configuration

```python
session = Session(
    max_retries=3,              # Number of retries
    retry_backoff_factor=0.3,   # Backoff between retries
    retry_on=[500, 502, 503],   # Status codes to retry
    timeout=30,                 # Default timeout in seconds
    pool_connections=10,        # Connection pool size
    pool_maxsize=50,           # Max connections per pool
)
```

## Request Options

```python
response = session.get(
    'https://api.example.com',
    params={'key': 'value'},           # URL parameters
    headers={'Authorization': 'token'}, # Headers
    timeout=10,                        # Timeout (seconds)
    allow_redirects=True,              # Follow redirects
    verify=True,                       # Verify SSL
    auth=('user', 'pass'),            # Basic auth
)
```

## Response Handling

```python
# Status
response.status_code         # 200
response.ok                  # True if 200-399
response.raise_for_status()  # Raise exception if error

# Content
response.text               # String content
response.content           # Bytes content
response.json()            # JSON decoded content

# Headers
response.headers           # Response headers dict
response.headers['Content-Type']  # Specific header

# Request info
response.url              # Final URL after redirects
response.request          # Request object
response.history          # Redirect history
```

## HTTP/2 and HTTP/3

```python
from requests_enhanced import HTTP2Adapter, HTTP3Adapter

# HTTP/2
http2_adapter = HTTP2Adapter()
session.mount("https://", http2_adapter)

# HTTP/3 with fallback
http3_adapter = HTTP3Adapter(fallback_to_http2=True)
session.mount("https://", http3_adapter)
```

## Error Handling

```python
from requests_enhanced.exceptions import (
    RequestException,        # Base exception
    RequestTimeoutError,     # Timeout occurred
    RequestRetryError,       # All retries failed
    ConnectionError,         # Connection issues
    HTTPError,              # HTTP error status
)

try:
    response = session.get(url)
    response.raise_for_status()
except RequestTimeoutError:
    print("Request timed out")
except RequestRetryError as e:
    print(f"Failed after retries: {e}")
except HTTPError as e:
    print(f"HTTP error: {e}")
except RequestException as e:
    print(f"Request failed: {e}")
```

## Common Patterns

### API Authentication

```python
# Bearer token
session.headers['Authorization'] = f'Bearer {token}'

# Basic auth
session.auth = ('username', 'password')

# Custom auth header
session.headers.update({
    'X-API-Key': 'your-api-key',
    'X-API-Secret': 'your-secret'
})
```

### Retry Configuration

```python
from urllib3.util.retry import Retry

# Custom retry strategy
retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"]
)

adapter = session.get_adapter("https://")
adapter.max_retries = retry_strategy
```

### File Upload

```python
# Single file
with open('file.txt', 'rb') as f:
    files = {'file': f}
    response = session.post(url, files=files)

# Multiple files
files = [
    ('files', ('file1.txt', open('file1.txt', 'rb'), 'text/plain')),
    ('files', ('file2.txt', open('file2.txt', 'rb'), 'text/plain'))
]
response = session.post(url, files=files)
```

### Streaming Response

```python
# Stream large responses
response = session.get(url, stream=True)
for chunk in response.iter_content(chunk_size=8192):
    process_chunk(chunk)

# Stream lines
for line in response.iter_lines():
    process_line(line)
```

### Cookie Management

```python
# Get cookies
cookies = session.cookies

# Set cookie
session.cookies.set('cookie_name', 'cookie_value')

# Use cookies dict
response = session.get(url, cookies={'session': 'xyz'})

# Save/load cookies
session.cookies.save('cookies.txt')
session.cookies.load('cookies.txt')
```

### Timeout Configuration

```python
# Single timeout value (both connect and read)
response = session.get(url, timeout=5)

# Separate connect and read timeouts
response = session.get(url, timeout=(3.05, 27))

# No timeout (not recommended)
response = session.get(url, timeout=None)
```

### Context Manager

```python
# Automatic cleanup
with Session() as session:
    response = session.get(url)
    # Session is closed automatically
```

### Performance Tips

```python
# Reuse sessions for multiple requests
session = Session()
for url in urls:
    response = session.get(url)  # Reuses connections

# Configure for high-volume requests
session = Session(
    pool_connections=25,
    pool_maxsize=100,
    max_retries=3
)

# Disable SSL verification (only for testing!)
response = session.get(url, verify=False)

# Use HTTP/2 for multiplexing
from requests_enhanced import HTTP2Adapter
session.mount("https://", HTTP2Adapter())
```

## Environment Variables

```bash
# Proxy configuration
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"
export NO_PROXY="localhost,127.0.0.1"

# Debugging
export REQUESTS_ENHANCED_DEBUG="1"
```

## Debugging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Log all HTTP traffic
import http.client
http.client.HTTPConnection.debuglevel = 1

# Inspect request before sending
req = session.prepare_request(session.get(url))
print(req.headers)
print(req.body)
```

## Comparison with requests

| Feature | requests | requests-enhanced |
|---------|----------|-------------------|
| HTTP/1.1 | ✅ | ✅ |
| HTTP/2 | ❌ | ✅ |
| HTTP/3 | ❌ | ✅ |
| Auto-retry | ❌ | ✅ |
| Enhanced exceptions | ❌ | ✅ |
| Better connection pooling | ❌ | ✅ |
| Backward compatible | - | ✅ |
