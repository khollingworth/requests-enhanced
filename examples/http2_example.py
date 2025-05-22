"""
HTTP/2 usage examples for requests-enhanced library.

This example demonstrates how to enable and use HTTP/2 protocol support
for improved performance through connection multiplexing, header compression,
and other HTTP/2 features.
"""

from typing import Dict, Any

from requests_enhanced import Session, HTTP2_AVAILABLE


def http2_session_example() -> Dict[str, Any]:
    """
    Example of using HTTP/2 with the Session class.

    Returns:
        Dict containing performance information and HTTP/2 availability
    """
    # Check if HTTP/2 is available
    if not HTTP2_AVAILABLE:
        print("HTTP/2 dependencies are not installed. Using HTTP/1.1 fallback.")
        print("Install HTTP/2 dependencies with: pip install requests-enhanced[http2]")

        # Create a standard HTTP/1.1 session when HTTP/2 is not available
        session = Session(http_version="1.1", timeout=(5, 30))
    else:
        print("HTTP/2 support is available and enabled.")
        try:
            # Create a session with HTTP/2 enabled
            session = Session(
                http_version="2",  # Request HTTP/2 protocol
                timeout=(5, 30),  # (connect_timeout, read_timeout)
            )
        except Exception as e:
            print(f"Error creating HTTP/2 session: {e}")
            print("Falling back to HTTP/1.1")
            session = Session(http_version="1.1", timeout=(5, 30))

    # Make a request to httpbin.org
    print("\nMaking request to httpbin.org...")
    try:
        response = session.get("https://httpbin.org/get?param=http2_test")
        print(f"Response status: {response.status_code}")
        return response.json()
    except Exception as e:
        print(f"Error making request: {e}")
        return {"error": str(e)}


def compare_protocols() -> None:
    """Compare HTTP/1.1 and HTTP/2 with multiple requests."""
    import time

    # URLs to test with - using httpbin as it supports both HTTP/1.1 and HTTP/2
    urls = [
        "https://httpbin.org/get?id=1",
        "https://httpbin.org/get?id=2",
        "https://httpbin.org/get?id=3",
        "https://httpbin.org/get?id=4",
        "https://httpbin.org/get?id=5",
    ]

    # Test with HTTP/1.1
    print("\nTesting with HTTP/1.1:")
    try:
        session_http1 = Session(http_version="1.1")
        start_time = time.time()

        for url in urls:
            try:
                response = session_http1.get(url)
                print(f"Request to {url} completed with status {response.status_code}")
            except Exception as e:
                print(f"Error with HTTP/1.1 request to {url}: {e}")

        http1_time = time.time() - start_time
        print(f"Total time for HTTP/1.1: {http1_time:.3f} seconds")
    except Exception as e:
        print(f"Error creating HTTP/1.1 session: {e}")
        http1_time = 0

    # Test with HTTP/2 if available
    http2_session_created = False
    if HTTP2_AVAILABLE:
        print("\nTesting with HTTP/2:")
        try:
            session_http2 = Session(http_version="2")
            http2_session_created = True
            start_time = time.time()

            for url in urls:
                try:
                    response = session_http2.get(url)
                    print(
                        f"Request to {url} completed with status {response.status_code}"
                    )
                except Exception as e:
                    print(f"Error with HTTP/2 request to {url}: {e}")

            http2_time = time.time() - start_time
            print(f"Total time for HTTP/2: {http2_time:.3f} seconds")
        except Exception as e:
            print(f"Error creating HTTP/2 session: {e}")
            print("Falling back to HTTP/1.1")
            http2_time = 0
            http2_session_created = False
    else:
        print("\nHTTP/2 dependencies not available - skipping HTTP/2 test")
        print("Install HTTP/2 dependencies with: pip install requests-enhanced[http2]")
        http2_time = 0

    # Calculate improvement
    if HTTP2_AVAILABLE and http2_session_created and http1_time > 0 and http2_time > 0:
        improvement = (http1_time - http2_time) / http1_time * 100
        print(f"\nHTTP/2 was {improvement:.1f}% faster than HTTP/1.1")
    elif not HTTP2_AVAILABLE:
        print("\nHTTP/2 dependencies not available - could not compare performance")
    elif http1_time == 0 or http2_time == 0:
        print("\nCould not compare performance due to errors in one or both protocols")


if __name__ == "__main__":
    print("HTTP/2 Example with requests-enhanced")
    print("=====================================")

    # Demonstrate basic HTTP/2 usage
    result = http2_session_example()
    print(f"Response data: {result}\n")

    # Compare HTTP/1.1 vs HTTP/2 performance
    compare_protocols()
