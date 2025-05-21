"""
Advanced retry and timeout handling examples for requests-enhanced library.
"""
from typing import Dict, Any
import logging
import requests
from requests.adapters import Retry
from requests_enhanced import Session
from requests_enhanced.exceptions import RequestRetryError, RequestTimeoutError
from requests_enhanced.logging import configure_logger


def configure_logging() -> None:
    """Configure the requests_enhanced logger for this example."""
    logger = logging.getLogger("requests_enhanced")
    # Configure with debug level and custom format
    configure_logger(
        logger,
        level=logging.DEBUG,
        log_format="%(asctime)s - %(levelname)s - %(message)s"
    )


def custom_retry_example() -> None:
    """Example of using custom retry configuration."""
    # Custom retry configuration
    retry_config = Retry(
        total=3,  # Total number of retries
        backoff_factor=0.5,  # Backoff factor between retries
        status_forcelist=[500, 502, 503, 504],  # Status codes to retry on
        allowed_methods=["GET", "POST"]  # HTTP methods to retry
    )
    
    # Create session with custom retry configuration
    session = Session(retry_config=retry_config)
    
    try:
        # This endpoint will return 503 Service Unavailable
        response = session.get("https://httpbin.org/status/503")
        print(f"Response status: {response.status_code}")
    except RequestRetryError as e:
        print(f"Retry failed: {e}")
        print(f"Original exception: {e.original_exception}")


def timeout_example() -> Dict[str, Any]:
    """Example of handling timeouts with requests-enhanced."""
    # Set custom timeout (connect_timeout, read_timeout)
    session = Session(timeout=(1.5, 3))
    
    try:
        # This endpoint simulates a 10-second delay
        response = session.get("https://httpbin.org/delay/10")
        return response.json()
    except RequestTimeoutError as e:
        print(f"Request timed out: {e}")
        print(f"Original exception: {e.original_exception}")
        return {"error": "timeout"}
    except requests.exceptions.ConnectionError as e:
        # Sometimes the ConnectionError is raised directly before it can be converted
        # to our custom RequestTimeoutError
        print(f"Request timed out or failed to connect: {e}")
        return {"error": "connection_or_timeout"}


if __name__ == "__main__":
    # Setup logging
    configure_logging()
    
    print("Custom Retry Example:")
    custom_retry_example()
    
    print("\nTimeout Example:")
    result = timeout_example()
    print(f"Result: {result}")