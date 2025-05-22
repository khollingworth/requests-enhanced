"""
Basic usage examples for requests-enhanced library.
"""

from requests_enhanced import Session
from requests_enhanced.utils import json_get, json_post


def session_example():
    """Example of using the Session class for HTTP requests."""
    # Create a session with default retry and timeout settings
    session = Session()

    # Simple GET request
    response = session.get("https://httpbin.org/get")
    print(f"GET Response Status: {response.status_code}")
    print(f"GET Response Content: {response.json()}")

    # POST request with JSON data
    data = {"name": "example", "value": 42}
    response = session.post("https://httpbin.org/post", json=data)
    print(f"\nPOST Response Status: {response.status_code}")
    print(f"POST Response Content: {response.json()}")


def utility_example():
    """Example of using utility functions for simpler requests."""
    # GET request with automatic JSON handling
    get_data = json_get("https://httpbin.org/get?param=value")
    print(f"\nUtility GET Result: {get_data}")

    # POST request with automatic JSON handling
    post_data = json_post("https://httpbin.org/post", data={"name": "example"})
    print(f"Utility POST Result: {post_data}")


if __name__ == "__main__":
    print("Session Examples:")
    session_example()

    print("\nUtility Function Examples:")
    utility_example()
