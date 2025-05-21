# Quickstart Guide

This guide will help you get started with the Requests Plus library.

## Installation

```bash
pip install requests-plus
```

## Basic Usage

```python
from requests_plus import Session

# Create a session with default retry and timeout settings
session = Session()

# Simple GET request
response = session.get("https://api.example.com/resources")
print(response.json())

# POST request with JSON data
data = {"name": "example", "value": 42}
response = session.post("https://api.example.com/resources", json=data)
print(response.status_code)
```

## Using Utility Functions

```python
from requests_plus.utils import json_get, json_post

# GET request that automatically returns JSON
data = json_get("https://api.example.com/resources")

# POST request with automatic JSON handling
result = json_post("https://api.example.com/resources", data={"name": "example"})
```