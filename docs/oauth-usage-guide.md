# OAuth Usage Guide for requests-enhanced

This guide demonstrates how to use OAuth 1.0/1.1 and OAuth 2.0 authentication with the `requests-enhanced` library.

## Installation

To use OAuth functionality, install the OAuth dependencies:

```bash
pip install requests-enhanced[oauth]
```

This installs the required `requests-oauthlib` and `oauthlib` packages.

## OAuth 1.0/1.1 Authentication

OAuth 1.0/1.1 is commonly used by APIs like Twitter, Flickr, and other services that require signature-based authentication.

### Basic Setup

```python
from requests_enhanced import OAuth1EnhancedSession

# Create an OAuth 1.0 session
session = OAuth1EnhancedSession(
    client_key='your_consumer_key',
    client_secret='your_consumer_secret'
)
```

### Complete OAuth 1.0 Flow

```python
from requests_enhanced import OAuth1EnhancedSession

# Step 1: Create session with consumer credentials
session = OAuth1EnhancedSession(
    client_key='your_consumer_key',
    client_secret='your_consumer_secret'
)

# Step 2: Fetch request token
request_token = session.fetch_request_token(
    'https://api.example.com/oauth/request_token'
)
print(f"Request Token: {request_token['oauth_token']}")

# Step 3: Get authorization URL
auth_url = session.authorization_url(
    'https://api.example.com/oauth/authorize'
)
print(f"Visit this URL to authorize: {auth_url}")

# Step 4: After user authorization, fetch access token
# (You'll get the verifier from the callback URL)
access_token = session.fetch_access_token(
    'https://api.example.com/oauth/access_token',
    verifier='verifier_from_callback'
)

# Step 5: Make authenticated requests
response = session.get('https://api.example.com/protected_resource')
print(response.json())
```

### Using Existing Access Tokens

If you already have access tokens, you can use them directly:

```python
from requests_enhanced import OAuth1EnhancedSession

session = OAuth1EnhancedSession(
    client_key='your_consumer_key',
    client_secret='your_consumer_secret',
    resource_owner_key='your_access_token',
    resource_owner_secret='your_access_token_secret'
)

# Make authenticated requests immediately
response = session.get('https://api.example.com/protected_resource')
```

### OAuth 1.0 with Enhanced Features

Combine OAuth with requests-enhanced features:

```python
from requests_enhanced import OAuth1EnhancedSession

session = OAuth1EnhancedSession(
    client_key='your_consumer_key',
    client_secret='your_consumer_secret',
    resource_owner_key='your_access_token',
    resource_owner_secret='your_access_token_secret',
    # Enhanced session features
    timeout=30,
    max_retries=3,
    http_version='2'  # Use HTTP/2
)

# Authenticated request with retry and timeout
response = session.get('https://api.example.com/data')
```

## OAuth 2.0 Authentication

OAuth 2.0 is used by modern APIs like Google, Facebook, GitHub, and many others.

### Basic Setup

```python
from requests_enhanced import OAuth2EnhancedSession

# Create an OAuth 2.0 session
session = OAuth2EnhancedSession(
    client_id='your_client_id'
)
```

### Authorization Code Flow

```python
from requests_enhanced import OAuth2EnhancedSession

# Step 1: Create session
session = OAuth2EnhancedSession(
    client_id='your_client_id',
    redirect_uri='https://your-app.com/callback',
    scope=['read', 'write']  # Requested scopes
)

# Step 2: Get authorization URL
auth_url, state = session.authorization_url(
    'https://api.example.com/oauth/authorize'
)
print(f"Visit this URL to authorize: {auth_url}")
print(f"State: {state}")

# Step 3: After user authorization, exchange code for token
# (You'll get the authorization_response from your callback URL)
token = session.fetch_token(
    'https://api.example.com/oauth/token',
    authorization_response='https://your-app.com/callback?code=auth_code&state=state',
    client_secret='your_client_secret'  # Required for confidential clients
)

# Step 4: Make authenticated requests
response = session.get('https://api.example.com/user')
print(response.json())
```

### Using Existing Tokens

If you already have an access token:

```python
from requests_enhanced import OAuth2EnhancedSession

token = {
    'access_token': 'your_access_token',
    'token_type': 'Bearer',
    'expires_in': 3600,
    'refresh_token': 'your_refresh_token'
}

session = OAuth2EnhancedSession(
    client_id='your_client_id',
    token=token
)

# Make authenticated requests
response = session.get('https://api.example.com/user')
```

### Token Refresh

Automatically refresh expired tokens:

```python
from requests_enhanced import OAuth2EnhancedSession

def save_token(token):
    """Callback to save updated tokens"""
    print(f"Token updated: {token}")
    # Save to database, file, etc.

session = OAuth2EnhancedSession(
    client_id='your_client_id',
    token=existing_token,
    auto_refresh_url='https://api.example.com/oauth/token',
    auto_refresh_kwargs={'client_secret': 'your_client_secret'},
    token_updater=save_token
)

# Tokens will be automatically refreshed when they expire
response = session.get('https://api.example.com/user')
```

### Manual Token Refresh

```python
from requests_enhanced import OAuth2EnhancedSession

session = OAuth2EnhancedSession(
    client_id='your_client_id',
    token=existing_token
)

# Manually refresh token
new_token = session.refresh_token(
    'https://api.example.com/oauth/token',
    client_secret='your_client_secret'
)
print(f"New token: {new_token}")
```

### OAuth 2.0 with Enhanced Features

```python
from requests_enhanced import OAuth2EnhancedSession

session = OAuth2EnhancedSession(
    client_id='your_client_id',
    token=token,
    # Enhanced session features
    timeout=45,
    max_retries=5,
    http_version='3'  # Use HTTP/3 if available
)

# Authenticated request with enhanced features
response = session.get('https://api.example.com/data')
```

## Client Credentials Flow (OAuth 2.0)

For server-to-server authentication:

```python
from requests_enhanced import OAuth2EnhancedSession

session = OAuth2EnhancedSession(client_id='your_client_id')

# Fetch token using client credentials
token = session.fetch_token(
    'https://api.example.com/oauth/token',
    client_secret='your_client_secret',
    grant_type='client_credentials',
    scope=['api:read', 'api:write']
)

# Make authenticated requests
response = session.get('https://api.example.com/data')
```

## Error Handling

```python
from requests_enhanced import OAuth1EnhancedSession, OAuth2EnhancedSession, OAuthNotAvailableError

try:
    # Check if OAuth is available
    session = OAuth1EnhancedSession(
        client_key='key',
        client_secret='secret'
    )
except OAuthNotAvailableError:
    print("OAuth dependencies not installed. Run: pip install requests-enhanced[oauth]")

# Handle OAuth-specific errors
from oauthlib.oauth2 import TokenExpiredError
from requests_oauthlib import TokenRequestDenied

try:
    response = session.get('https://api.example.com/data')
except TokenExpiredError:
    print("Token expired, need to refresh")
except TokenRequestDenied as e:
    print(f"Token request denied: {e}")
```

## Best Practices

### 1. Secure Token Storage

```python
import json
import os
from pathlib import Path

def save_token_to_file(token, filename='token.json'):
    """Securely save token to file"""
    token_path = Path.home() / '.config' / 'myapp' / filename
    token_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(token_path, 'w') as f:
        json.dump(token, f)
    
    # Set restrictive permissions
    os.chmod(token_path, 0o600)

def load_token_from_file(filename='token.json'):
    """Load token from file"""
    token_path = Path.home() / '.config' / 'myapp' / filename
    
    if token_path.exists():
        with open(token_path, 'r') as f:
            return json.load(f)
    return None
```

### 2. Environment Variables for Secrets

```python
import os
from requests_enhanced import OAuth2EnhancedSession

session = OAuth2EnhancedSession(
    client_id=os.getenv('OAUTH_CLIENT_ID'),
    client_secret=os.getenv('OAUTH_CLIENT_SECRET'),  # Never hardcode secrets
    redirect_uri=os.getenv('OAUTH_REDIRECT_URI')
)
```

### 3. Robust Error Handling

```python
from requests_enhanced import OAuth2EnhancedSession
from requests.exceptions import RequestException
from oauthlib.oauth2 import TokenExpiredError
import time

def make_authenticated_request(session, url, max_retries=3):
    """Make request with automatic token refresh and retry logic"""
    for attempt in range(max_retries):
        try:
            response = session.get(url)
            response.raise_for_status()
            return response.json()
            
        except TokenExpiredError:
            # Token expired, refresh it
            session.refresh_token(
                'https://api.example.com/oauth/token',
                client_secret=os.getenv('OAUTH_CLIENT_SECRET')
            )
            continue
            
        except RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
            continue
    
    raise Exception("Max retries exceeded")
```

### 4. Session Reuse

```python
from requests_enhanced import OAuth2EnhancedSession

class APIClient:
    def __init__(self, client_id, client_secret):
        self.session = OAuth2EnhancedSession(
            client_id=client_id,
            auto_refresh_url='https://api.example.com/oauth/token',
            auto_refresh_kwargs={'client_secret': client_secret},
            token_updater=self._save_token
        )
        
        # Load existing token if available
        token = self._load_token()
        if token:
            self.session.token = token
    
    def _save_token(self, token):
        # Implement token persistence
        pass
    
    def _load_token(self):
        # Implement token loading
        pass
    
    def get_user_data(self):
        return self.session.get('https://api.example.com/user').json()
    
    def get_posts(self):
        return self.session.get('https://api.example.com/posts').json()
```

## Common OAuth Providers

### GitHub

```python
from requests_enhanced import OAuth2EnhancedSession

session = OAuth2EnhancedSession(
    client_id='your_github_client_id',
    redirect_uri='http://localhost:8080/callback',
    scope=['user', 'repo']
)

# Authorization URL
auth_url, state = session.authorization_url(
    'https://github.com/login/oauth/authorize'
)

# Token exchange
token = session.fetch_token(
    'https://github.com/login/oauth/access_token',
    authorization_response=callback_url,
    client_secret='your_github_client_secret'
)

# API requests
user = session.get('https://api.github.com/user').json()
repos = session.get('https://api.github.com/user/repos').json()
```

### Google

```python
from requests_enhanced import OAuth2EnhancedSession

session = OAuth2EnhancedSession(
    client_id='your_google_client_id',
    redirect_uri='http://localhost:8080/callback',
    scope=['openid', 'email', 'profile']
)

# Authorization URL with additional parameters
auth_url, state = session.authorization_url(
    'https://accounts.google.com/o/oauth2/auth',
    access_type='offline',  # For refresh tokens
    prompt='consent'
)

# Token exchange
token = session.fetch_token(
    'https://oauth2.googleapis.com/token',
    authorization_response=callback_url,
    client_secret='your_google_client_secret'
)

# API requests
profile = session.get('https://www.googleapis.com/oauth2/v2/userinfo').json()
```

### Twitter (OAuth 1.0a)

```python
from requests_enhanced import OAuth1EnhancedSession

session = OAuth1EnhancedSession(
    client_key='your_twitter_api_key',
    client_secret='your_twitter_api_secret'
)

# Request token
request_token = session.fetch_request_token(
    'https://api.twitter.com/oauth/request_token',
    realm='your_app_name'
)

# Authorization URL
auth_url = session.authorization_url(
    'https://api.twitter.com/oauth/authorize'
)

# Access token (after user authorization)
access_token = session.fetch_access_token(
    'https://api.twitter.com/oauth/access_token',
    verifier='pin_from_user'
)

# API requests
user = session.get('https://api.twitter.com/1.1/account/verify_credentials.json').json()
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```
   OAuthNotAvailableError: OAuth functionality requires 'requests-oauthlib' package
   ```
   Solution: `pip install requests-enhanced[oauth]`

2. **Invalid Client Credentials**
   ```
   oauthlib.oauth2.rfc6749.errors.InvalidClientError
   ```
   Solution: Verify your client ID and secret

3. **Token Expired**
   ```
   oauthlib.oauth2.rfc6749.errors.TokenExpiredError
   ```
   Solution: Implement automatic token refresh

4. **Invalid Redirect URI**
   ```
   oauthlib.oauth2.rfc6749.errors.MismatchingStateError
   ```
   Solution: Ensure redirect URI matches exactly what's registered

### Debug Mode

Enable debug logging to troubleshoot OAuth issues:

```python
import logging
from requests_enhanced import OAuth2EnhancedSession

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

session = OAuth2EnhancedSession(client_id='your_client_id')
# OAuth requests will now show detailed debug information
```

## Migration from requests-oauthlib

If you're migrating from `requests-oauthlib`, the API is largely compatible:

```python
# Old: requests-oauthlib
from requests_oauthlib import OAuth1Session, OAuth2Session

# New: requests-enhanced
from requests_enhanced import OAuth1EnhancedSession, OAuth2EnhancedSession

# The API is the same, but you get additional enhanced features
session = OAuth2EnhancedSession(
    client_id='client_id',
    # Plus enhanced features:
    timeout=30,
    max_retries=3,
    http_version='2'
)
```

For more information, see the [API Reference](api-reference.md) and [Examples](examples/) directory.
