#!/usr/bin/env python3
"""
Advanced Session Management Example

This example demonstrates advanced features of requests-enhanced sessions including:
- Connection pooling configuration
- Custom retry strategies
- Session persistence
- Cookie management
- Connection adapters
"""

import time
from requests_enhanced import Session, HTTP2Adapter, HTTP3Adapter
from requests_enhanced.adapters import HTTP3_AVAILABLE
from urllib3.util.retry import Retry


def connection_pooling_example():
    """Example: Configure connection pooling for better performance."""
    print("=== Connection Pooling Example ===")

    # Create session with custom pool configuration
    session = Session(
        pool_connections=20,  # Number of connection pools to cache
        pool_maxsize=50,  # Maximum number of connections to save in the pool
        max_retries=3,
    )

    # Make multiple requests to demonstrate connection reuse
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/headers",
        "https://httpbin.org/user-agent",
    ]

    print("Making multiple requests with connection pooling...")
    start_time = time.time()

    for i, url in enumerate(urls * 3):  # Repeat URLs to show reuse
        response = session.get(url)
        print(f"Request {i+1}: {response.status_code} - {url}")

    elapsed = time.time() - start_time
    print(f"Total time for 9 requests: {elapsed:.2f} seconds")
    print("(Connection pooling reduces overhead by reusing connections)")


def custom_retry_strategy_example():
    """Example: Implement custom retry strategies."""
    print("\n=== Custom Retry Strategy Example ===")

    # Define a custom retry strategy
    custom_retry = Retry(
        total=5,  # Total number of retries
        backoff_factor=0.5,  # Backoff factor between retries
        status_forcelist=[500, 502, 503, 504],  # Retry on these status codes
        allowed_methods=["GET", "POST", "PUT"],  # Methods to retry
        respect_retry_after_header=True,  # Respect Retry-After header
    )

    # Create session with custom retry
    session = Session()

    # Apply custom retry to HTTP adapter
    adapter = session.get_adapter("https://")
    adapter.max_retries = custom_retry

    print("Testing custom retry strategy...")
    try:
        # This endpoint returns 500 errors randomly
        response = session.get("https://httpbin.org/status/500,200")
        print(f"Success after retries! Status: {response.status_code}")
    except Exception as e:
        print(f"Failed even after custom retries: {e}")


def multi_protocol_session_example():
    """Example: Use different HTTP protocols in the same session."""
    print("\n=== Multi-Protocol Session Example ===")

    session = Session()

    # Mount different adapters for different protocols
    http2_adapter = HTTP2Adapter()
    session.mount("https://http2.pro", http2_adapter)

    if HTTP3_AVAILABLE:
        http3_adapter = HTTP3Adapter()
        session.mount("https://quic.tech", http3_adapter)
        print("HTTP/3 adapter mounted for quic.tech")
    else:
        print("HTTP/3 not available, using HTTP/2 fallback")

    # Test different endpoints
    test_endpoints = [
        ("https://httpbin.org/get", "Standard HTTPS"),
        ("https://http2.pro/api/v1", "HTTP/2 endpoint"),
    ]

    for url, description in test_endpoints:
        try:
            print(f"\nTesting {description}: {url}")
            response = session.get(url, timeout=5)
            print(f"Status: {response.status_code}")
            print(
                f"Protocol: {response.raw.version if hasattr(response.raw, 'version') else 'HTTP/1.1'}"
            )
        except Exception as e:
            print(f"Error: {e}")


def session_cookie_management_example():
    """Example: Managing cookies across requests."""
    print("\n=== Cookie Management Example ===")

    session = Session()

    # Set initial cookies
    session.cookies.set("session_id", "abc123", domain=".httpbin.org")
    session.cookies.set("user_pref", "dark_mode", domain=".httpbin.org")

    print("Initial cookies:")
    for cookie in session.cookies:
        print(f"  {cookie.name}: {cookie.value}")

    # Make request that sets additional cookies
    print("\nMaking request to set cookies...")
    response = session.get("https://httpbin.org/cookies/set/test_cookie/test_value")

    print("\nCookies after request:")
    for cookie in session.cookies:
        print(f"  {cookie.name}: {cookie.value}")

    # Verify cookies are sent in subsequent requests
    print("\nVerifying cookies in next request...")
    response = session.get("https://httpbin.org/cookies")
    cookies_received = response.json()["cookies"]
    print("Server received cookies:", cookies_received)


def session_persistence_example():
    """Example: Persist session configuration across requests."""
    print("\n=== Session Persistence Example ===")

    # Create a base session with common configuration
    base_session = Session(
        max_retries=3,
        timeout=10,
        headers={
            "User-Agent": "MyApp/1.0",
            "Accept": "application/json",
            "X-API-Version": "2.0",
        },
    )

    # Add authentication
    base_session.auth = ("username", "password")  # Basic auth example

    print("Base session configuration:")
    print(f"  Max retries: {base_session.max_retries}")
    print(f"  Timeout: {base_session.timeout}")
    print(f"  Headers: {dict(base_session.headers)}")

    # Use the session for multiple API endpoints
    endpoints = ["/user", "/posts", "/comments"]

    print("\nMaking requests with persistent configuration...")
    for endpoint in endpoints:
        try:
            # Using httpbin to echo our request details
            response = base_session.get(f"https://httpbin.org{endpoint}")
            print(f"  {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"  {endpoint}: Error - {e}")


def context_manager_example():
    """Example: Using session as a context manager."""
    print("\n=== Context Manager Example ===")

    print("Using session as context manager ensures proper cleanup...")

    # Session is automatically closed when exiting the context
    with Session(max_retries=2, timeout=5) as session:
        # Configure session
        session.headers.update({"X-Session-Type": "Temporary"})

        # Make requests
        response = session.get("https://httpbin.org/headers")
        headers = response.json()["headers"]
        print(f"Custom header received: {headers.get('X-Session-Type', 'Not found')}")

    print("Session automatically closed after context exit")


def performance_monitoring_example():
    """Example: Monitor session performance and connection reuse."""
    print("\n=== Performance Monitoring Example ===")

    session = Session(pool_connections=10, pool_maxsize=20, max_retries=1)

    # Add timing to requests
    def time_request(session, url):
        start = time.time()
        response = session.get(url)
        elapsed = time.time() - start
        return elapsed, response.status_code

    # Make multiple requests to same host
    print("Testing connection reuse performance...")
    url = "https://httpbin.org/delay/0"

    times = []
    for i in range(5):
        elapsed, status = time_request(session, url)
        times.append(elapsed)
        print(f"Request {i+1}: {elapsed:.3f}s (Status: {status})")

    print(f"\nAverage time: {sum(times)/len(times):.3f}s")
    print(f"First request: {times[0]:.3f}s (includes connection setup)")
    print(f"Subsequent avg: {sum(times[1:])/len(times[1:]):.3f}s (reuses connection)")


def main():
    """Run all advanced session examples."""
    print("requests-enhanced Advanced Session Examples")
    print("=" * 50)

    connection_pooling_example()
    custom_retry_strategy_example()
    multi_protocol_session_example()
    session_cookie_management_example()
    session_persistence_example()
    context_manager_example()
    performance_monitoring_example()

    print("\n" + "=" * 50)
    print("Advanced examples completed!")


if __name__ == "__main__":
    main()
