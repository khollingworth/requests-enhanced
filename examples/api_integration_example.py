#!/usr/bin/env python3
"""
API Integration Example - Using requests-enhanced with real APIs

This example demonstrates how to use requests-enhanced for common API integration
patterns including authentication, pagination, and error handling.
"""

import json
import os
from requests_enhanced import Session
from requests_enhanced.exceptions import RequestRetryError, RequestTimeoutError


def github_api_example():
    """Example: Interacting with GitHub API."""
    print("=== GitHub API Example ===")

    # Create a session with automatic retries
    from urllib3.util.retry import Retry

    retry = Retry(total=3, backoff_factor=0.5)
    session = Session(retry_config=retry, timeout=(3.05, 30))

    # Optional: Add authentication if you have a token
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        session.headers.update({"Authorization": f"token {github_token}"})

    try:
        # Get information about a repository
        response = session.get("https://api.github.com/repos/python/cpython")
        repo_data = response.json()

        print(f"Repository: {repo_data['full_name']}")
        print(f"Stars: {repo_data['stargazers_count']:,}")
        print(f"Forks: {repo_data['forks_count']:,}")
        print(f"Language: {repo_data['language']}")

    except RequestRetryError as e:
        print(f"Failed after retries: {e}")
    except RequestTimeoutError as e:
        print(f"Request timed out: {e}")


def paginated_api_example():
    """Example: Handling paginated API responses."""
    print("\n=== Paginated API Example ===")

    session = Session(max_retries=2, timeout=10)

    # Example: Get multiple pages of GitHub users
    all_users = []
    page = 1
    max_pages = 3  # Limit for this example

    while page <= max_pages:
        try:
            response = session.get(
                "https://api.github.com/users",
                params={"per_page": 10, "since": page * 10},
            )
            users = response.json()

            if not users:
                break

            all_users.extend(users)
            print(f"Fetched page {page}: {len(users)} users")
            page += 1

        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break

    print(f"Total users fetched: {len(all_users)}")
    print(f"First user: {all_users[0]['login'] if all_users else 'None'}")


def rest_api_crud_example():
    """Example: CRUD operations with a REST API."""
    print("\n=== REST API CRUD Example ===")

    # Using JSONPlaceholder as a test API
    base_url = "https://jsonplaceholder.typicode.com"
    from urllib3.util.retry import Retry

    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],  # Retry on server errors
    )
    session = Session(retry_config=retry, timeout=10)

    # CREATE - Post a new resource
    new_post = {
        "title": "Test Post from requests-enhanced",
        "body": "This is a test post using requests-enhanced library",
        "userId": 1,
    }

    try:
        print("Creating new post...")
        response = session.post(f"{base_url}/posts", json=new_post)
        created_post = response.json()
        print(f"Created post with ID: {created_post['id']}")

        # READ - Get the post
        print("\nReading post...")
        response = session.get(f"{base_url}/posts/1")
        post = response.json()
        print(f"Post title: {post['title']}")

        # UPDATE - Modify the post
        print("\nUpdating post...")
        updated_data = {"title": "Updated Title"}
        response = session.patch(f"{base_url}/posts/1", json=updated_data)
        print(f"Update status code: {response.status_code}")

        # DELETE - Remove the post
        print("\nDeleting post...")
        response = session.delete(f"{base_url}/posts/1")
        print(f"Delete status code: {response.status_code}")

    except RequestRetryError as e:
        print(f"API request failed: {e}")


def api_with_custom_headers():
    """Example: Using custom headers and authentication."""
    print("\n=== Custom Headers Example ===")

    session = Session(max_retries=2)

    # Add custom headers
    session.headers.update(
        {
            "User-Agent": "requests-enhanced/0.1.12",
            "Accept": "application/json",
            "X-Custom-Header": "CustomValue",
        }
    )

    # Example: httpbin.org echo service
    try:
        response = session.get("https://httpbin.org/headers")
        headers_echo = response.json()

        print("Headers sent to server:")
        for key, value in headers_echo["headers"].items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"Error: {e}")


def error_handling_example():
    """Example: Comprehensive error handling."""
    print("\n=== Error Handling Example ===")

    from urllib3.util.retry import Retry

    retry = Retry(total=2, backoff_factor=1.0)
    session = Session(retry_config=retry, timeout=5)

    # Test different error scenarios
    test_urls = [
        ("https://httpbin.org/delay/10", "Timeout example"),
        ("https://httpbin.org/status/500", "Server error example"),
        ("https://invalid-domain-that-does-not-exist.com", "DNS error example"),
    ]

    for url, description in test_urls:
        print(f"\nTesting: {description}")
        print(f"URL: {url}")

        try:
            response = session.get(url)
            print(f"Success! Status code: {response.status_code}")
        except RequestTimeoutError as e:
            print(f"Timeout error: Request took too long")
            print(f"Details: {e}")
        except RequestRetryError as e:
            print(f"Retry error: Failed after {session.max_retries} attempts")
            print(f"Details: {e}")
        except Exception as e:
            print(f"Unexpected error: {type(e).__name__}")
            print(f"Details: {e}")


def main():
    """Run all API integration examples."""
    print("requests-enhanced API Integration Examples")
    print("=" * 50)

    # Run examples
    github_api_example()
    paginated_api_example()
    rest_api_crud_example()
    api_with_custom_headers()
    error_handling_example()

    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    main()
