"""
HTTP/3 usage examples for requests-enhanced library with fallback capability.

This example demonstrates how to enable and use HTTP/3 protocol support
with automatic fallback to HTTP/2 and HTTP/1.1 if the server or dependencies
don't support HTTP/3.
"""

from typing import Dict, Any
import time

from requests_enhanced import Session, HTTP3_AVAILABLE, HTTP2_AVAILABLE


def http3_session_example() -> Dict[str, Any]:
    """
    Example of using HTTP/3 with automatic fallback mechanism.

    Returns:
        Dict containing performance information and protocol availability
    """
    # Check HTTP/3 and HTTP/2 availability
    protocol_support = {
        "HTTP/3 available": HTTP3_AVAILABLE,
        "HTTP/2 available": HTTP2_AVAILABLE,
    }

    print(f"Protocol support: {protocol_support}")

    if not HTTP3_AVAILABLE:
        print("HTTP/3 dependencies are not installed. Automatic fallback will occur.")
        print("Install HTTP/3 dependencies with: pip install requests-enhanced[http3]")

    try:
        # Create a session with HTTP/3 enabled and automatic fallback
        session = Session(
            http_version="3",  # Request HTTP/3 protocol with fallback
            timeout=(5, 30),  # (connect_timeout, read_timeout)
        )

        print("\nCreated session with HTTP/3 requested (with automatic fallback)")

        # Make a request to a site that supports HTTP/3
        print("\nMaking request to Cloudflare (supports HTTP/3)...")
        start_time = time.time()
        response = session.get("https://cloudflare.com/")
        cf_time = time.time() - start_time
        print(f"Response status: {response.status_code}")
        print(f"Request completed in {cf_time:.3f} seconds")

        # Make a request to httpbin (may not support HTTP/3)
        print("\nMaking request to httpbin.org...")
        start_time = time.time()
        response = session.get("https://httpbin.org/get?param=http3_test")
        httpbin_time = time.time() - start_time
        print(f"Response status: {response.status_code}")
        print(f"Request completed in {httpbin_time:.3f} seconds")

        return {
            "protocol_support": protocol_support,
            "cloudflare_time": cf_time,
            "httpbin_time": httpbin_time,
            "cloudflare_status": response.status_code,
        }

    except Exception as e:
        print(f"Error in HTTP/3 session example: {e}")
        return {"error": str(e), "protocol_support": protocol_support}


def compare_protocols() -> None:
    """Compare HTTP/1.1, HTTP/2, and HTTP/3 with multiple requests."""
    # URLs to test with - using sites that support various protocols
    urls = [
        "https://cloudflare.com",
        "https://google.com",
        "https://facebook.com",
        "https://github.com",
    ]

    protocols = []
    times = {}

    # Test with HTTP/1.1
    print("\nTesting with HTTP/1.1:")
    try:
        session_http1 = Session(http_version="1.1")
        protocols.append("1.1")

        start_time = time.time()
        for url in urls:
            try:
                response = session_http1.get(url)
                print(f"Request to {url} completed with status {response.status_code}")
            except Exception as e:
                print(f"Error with HTTP/1.1 request to {url}: {e}")

        http1_time = time.time() - start_time
        times["1.1"] = http1_time
        print(f"Total time for HTTP/1.1: {http1_time:.3f} seconds")
    except Exception as e:
        print(f"Error creating HTTP/1.1 session: {e}")

    # Test with HTTP/2 if available
    if HTTP2_AVAILABLE:
        print("\nTesting with HTTP/2:")
        try:
            session_http2 = Session(http_version="2")
            protocols.append("2")

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
            times["2"] = http2_time
            print(f"Total time for HTTP/2: {http2_time:.3f} seconds")
        except Exception as e:
            print(f"Error creating HTTP/2 session: {e}")
    else:
        print("\nHTTP/2 dependencies not available - skipping HTTP/2 test")
        print("Install HTTP/2 dependencies with: pip install requests-enhanced[http2]")

    # Test with HTTP/3 if available
    if HTTP3_AVAILABLE:
        print("\nTesting with HTTP/3:")
        try:
            session_http3 = Session(http_version="3")
            protocols.append("3")

            start_time = time.time()
            for url in urls:
                try:
                    response = session_http3.get(url)
                    print(
                        f"Request to {url} completed with status {response.status_code}"
                    )
                except Exception as e:
                    print(f"Error with HTTP/3 request to {url}: {e}")

            http3_time = time.time() - start_time
            times["3"] = http3_time
            print(f"Total time for HTTP/3: {http3_time:.3f} seconds")
        except Exception as e:
            print(f"Error creating HTTP/3 session: {e}")
    else:
        print("\nHTTP/3 dependencies not available - skipping HTTP/3 test")
        print("Install HTTP/3 dependencies with: pip install requests-enhanced[http3]")

    # Calculate and display improvements
    print("\nPerformance comparison:")

    # Sort protocols to ensure HTTP/1.1 is the baseline
    protocols.sort()

    if "1.1" in protocols and len(protocols) > 1:
        baseline = times["1.1"]
        for proto in protocols:
            if proto == "1.1":
                continue

            if proto in times and times[proto] > 0:
                improvement = (baseline - times[proto]) / baseline * 100
                if improvement > 0:
                    print(f"HTTP/{proto} was {improvement:.1f}% faster than HTTP/1.1")
                else:
                    print(f"HTTP/{proto} was {-improvement:.1f}% slower than HTTP/1.1")

    # Compare HTTP/3 to HTTP/2 if both are available
    if "2" in protocols and "3" in protocols:
        if times["2"] > 0 and times["3"] > 0:
            improvement = (times["2"] - times["3"]) / times["2"] * 100
            if improvement > 0:
                print(f"HTTP/3 was {improvement:.1f}% faster than HTTP/2")
            else:
                print(f"HTTP/3 was {-improvement:.1f}% slower than HTTP/2")


if __name__ == "__main__":
    print("HTTP/3 Example with Automatic Fallback in requests-enhanced")
    print("=========================================================")

    # Demonstrate basic HTTP/3 usage with fallback
    result = http3_session_example()
    print(f"\nResponse data: {result}\n")

    # Compare HTTP/1.1 vs HTTP/2 vs HTTP/3 performance
    compare_protocols()
