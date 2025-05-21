# Requests Enhanced

[![CI](https://github.com/khollingworth/requests-enhanced/actions/workflows/ci.yml/badge.svg)](https://github.com/khollingworth/requests-enhanced/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/requests-enhanced.svg)](https://badge.fury.io/py/requests-enhanced)
[![Python Versions](https://img.shields.io/pypi/pyversions/requests-enhanced.svg)](https://pypi.org/project/requests-enhanced/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

An enhanced wrapper for the popular `requests` library with additional features for improved reliability and convenience in Python HTTP requests.

## Features

- **Automatic Retries**: Built-in retry mechanism with configurable backoff strategy
- **Timeout Handling**: Enhanced timeout configuration and error handling
- **Improved Logging**: Customizable logging with formatted output
- **Utility Functions**: Simplified JSON request handling

## Installation

```bash
# From PyPI
pip install requests-enhanced

# From source (development)
git clone https://github.com/khollingworth/requests-enhanced.git
cd requests-enhanced
pip install -e ".[dev]"
```

## Quick Start

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
```

## Utility Functions

For quick, one-off requests:

```python
from requests_enhanced.utils import json_get, json_post

# GET request that automatically returns JSON
data = json_get("https://api.example.com/resources")

# POST request with automatic JSON handling
result = json_post("https://api.example.com/resources", data={"name": "example"})
```

## Error Handling

```python
from requests_enhanced import Session
from requests_enhanced.exceptions import RequestTimeoutError, RequestRetryError

try:
    session = Session()
    response = session.get("https://api.example.com/resources")
except RequestTimeoutError as e:
    print(f"Request timed out: {e}")
    print(f"Original exception: {e.original_exception}")
except RequestRetryError as e:
    print(f"Retry failed: {e}")
```

## Documentation

Detailed documentation is available in the [docs](docs/) directory:

- [Quickstart Guide](docs/quickstart.md): Get up and running quickly
- [Usage Guide](docs/usage.md): Detailed usage examples and patterns
- [API Reference](docs/api_reference.md): Complete API documentation

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/khollingworth/requests-enhanced.git
cd requests-enhanced

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/requests_plus --cov-report=term-missing

# Run specific test file
pytest tests/test_sessions.py
```

### Code Style

This project uses black for code formatting and flake8 for linting:

```bash
# Format code
black src tests examples

# Check code style
flake8 src tests examples
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.