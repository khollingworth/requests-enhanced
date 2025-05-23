#!/usr/bin/env python3
"""
OAuth Examples for requests-enhanced

This module demonstrates how to use OAuth 1.0/1.1 and OAuth 2.0 authentication
with the requests-enhanced library.

Requirements:
    pip install requests-enhanced[oauth]
"""

import os
import json
from pathlib import Path

try:
    from requests_enhanced import (
        OAuth1EnhancedSession,
        OAuth2EnhancedSession,
        OAUTH_AVAILABLE,
    )

    if not OAUTH_AVAILABLE:
        raise ImportError("OAuth dependencies not available")
except ImportError:
    print("OAuth functionality requires: pip install requests-enhanced[oauth]")
    exit(1)


def oauth1_twitter_example():
    """
    Example: OAuth 1.0a with Twitter API

    Note: This is a demonstration. You'll need actual Twitter API credentials.
    """
    print("=== OAuth 1.0a Twitter Example ===")

    # Twitter API credentials (use environment variables in production)
    consumer_key = os.getenv("TWITTER_CONSUMER_KEY", "your_consumer_key")
    consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET", "your_consumer_secret")

    if consumer_key == "your_consumer_key":
        print(
            "⚠️  Set TWITTER_CONSUMER_KEY and TWITTER_CONSUMER_SECRET environment variables"
        )
        print("   This example will show the OAuth flow without making real requests")

    # Step 1: Create OAuth 1.0 session
    session = OAuth1EnhancedSession(
        client_key=consumer_key,
        client_secret=consumer_secret,
        # Enhanced features
        timeout=30,
        max_retries=3,
    )

    try:
        # Step 2: Fetch request token
        print("📝 Fetching request token...")
        request_token = session.fetch_request_token(
            "https://api.twitter.com/oauth/request_token", realm="YourAppName"
        )
        print(f"✅ Request token: {request_token.get('oauth_token', 'N/A')}")

        # Step 3: Get authorization URL
        auth_url = session.authorization_url("https://api.twitter.com/oauth/authorize")
        print(f"🔗 Authorization URL: {auth_url}")
        print("   User should visit this URL and authorize the application")

        # Step 4: Exchange for access token (after user authorization)
        # In a real app, you'd get the verifier from the callback
        verifier = input(
            "Enter the PIN/verifier from Twitter (or press Enter to skip): "
        ).strip()

        if verifier:
            access_token = session.fetch_access_token(
                "https://api.twitter.com/oauth/access_token", verifier=verifier
            )
            print(f"✅ Access token: {access_token.get('oauth_token', 'N/A')}")

            # Step 5: Make authenticated requests
            print("📊 Making authenticated request...")
            response = session.get(
                "https://api.twitter.com/1.1/account/verify_credentials.json"
            )
            if response.status_code == 200:
                user_data = response.json()
                print(
                    f"✅ Authenticated as: @{user_data.get('screen_name', 'unknown')}"
                )
            else:
                print(f"❌ Request failed: {response.status_code}")
        else:
            print("⏭️  Skipping access token exchange")

    except Exception as e:
        print(f"❌ OAuth 1.0 flow error: {e}")
        print("   This is expected without real credentials")


def oauth2_github_example():
    """
    Example: OAuth 2.0 with GitHub API

    Note: This is a demonstration. You'll need actual GitHub OAuth app credentials.
    """
    print("\n=== OAuth 2.0 GitHub Example ===")

    # GitHub OAuth app credentials
    client_id = os.getenv("GITHUB_CLIENT_ID", "your_github_client_id")
    client_secret = os.getenv("GITHUB_CLIENT_SECRET", "your_github_client_secret")
    redirect_uri = "http://localhost:8080/callback"

    if client_id == "your_github_client_id":
        print("⚠️  Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET environment variables")
        print("   This example will show the OAuth flow without making real requests")

    # Step 1: Create OAuth 2.0 session
    session = OAuth2EnhancedSession(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=["user", "repo"],
        # Enhanced features
        timeout=30,
        max_retries=3,
        http_version="2",  # Use HTTP/2 for better performance
    )

    try:
        # Step 2: Get authorization URL
        print("📝 Generating authorization URL...")
        auth_url, state = session.authorization_url(
            "https://github.com/login/oauth/authorize",
            # Additional parameters
            access_type="offline",
        )
        print(f"🔗 Authorization URL: {auth_url}")
        print(f"🔒 State: {state}")
        print("   User should visit this URL and authorize the application")

        # Step 3: Exchange authorization code for token
        # In a real app, you'd get this from your callback endpoint
        auth_response = input(
            "Enter the full callback URL (or press Enter to skip): "
        ).strip()

        if auth_response:
            print("🔄 Exchanging authorization code for token...")
            token = session.fetch_token(
                "https://github.com/login/oauth/access_token",
                authorization_response=auth_response,
                client_secret=client_secret,
            )
            print(
                f"✅ Access token received (expires in {token.get('expires_in', 'N/A')} seconds)"
            )

            # Step 4: Make authenticated requests
            print("📊 Making authenticated requests...")

            # Get user info
            user_response = session.get("https://api.github.com/user")
            if user_response.status_code == 200:
                user_data = user_response.json()
                print(f"✅ Authenticated as: {user_data.get('login', 'unknown')}")
                print(f"   Name: {user_data.get('name', 'N/A')}")
                print(f"   Public repos: {user_data.get('public_repos', 'N/A')}")

            # Get repositories
            repos_response = session.get("https://api.github.com/user/repos?per_page=5")
            if repos_response.status_code == 200:
                repos = repos_response.json()
                print(f"📚 Recent repositories:")
                for repo in repos[:3]:
                    print(f"   - {repo['name']} ({repo['language'] or 'Unknown'})")

        else:
            print("⏭️  Skipping token exchange")

    except Exception as e:
        print(f"❌ OAuth 2.0 flow error: {e}")
        print("   This is expected without real credentials")


def oauth2_token_management_example():
    """
    Example: OAuth 2.0 token management and refresh
    """
    print("\n=== OAuth 2.0 Token Management ===")

    # Simulate an existing token (in practice, load from secure storage)
    existing_token = {
        "access_token": "example_access_token",
        "refresh_token": "example_refresh_token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": ["user", "repo"],
    }

    # Token storage functions
    def save_token(token):
        """Save token to secure storage"""
        print(f"💾 Saving updated token: {token.get('access_token', 'N/A')[:10]}...")
        # In practice: save to database, keychain, etc.
        token_file = Path.home() / ".config" / "myapp" / "github_token.json"
        token_file.parent.mkdir(parents=True, exist_ok=True)
        with open(token_file, "w") as f:
            json.dump(token, f)
        os.chmod(token_file, 0o600)  # Secure permissions

    def load_token():
        """Load token from secure storage"""
        token_file = Path.home() / ".config" / "myapp" / "github_token.json"
        if token_file.exists():
            with open(token_file, "r") as f:
                return json.load(f)
        return None

    # Create session with automatic token refresh
    session = OAuth2EnhancedSession(
        client_id="your_client_id",
        token=existing_token,
        auto_refresh_url="https://github.com/login/oauth/access_token",
        auto_refresh_kwargs={"client_secret": "your_client_secret"},
        token_updater=save_token,  # Automatically save refreshed tokens
    )

    print("🔧 Session configured with automatic token refresh")
    print("   Tokens will be automatically refreshed when they expire")

    # Manual token refresh example
    try:
        print("🔄 Manually refreshing token...")
        new_token = session.refresh_token(
            "https://github.com/login/oauth/access_token",
            client_secret="your_client_secret",
        )
        print("✅ Token refreshed successfully")

    except Exception as e:
        print(f"❌ Token refresh failed: {e}")
        print("   This is expected without real credentials")

    # Token property management
    print("\n🔧 Token property management:")
    print(f"   Current token: {session.token}")

    # Set new token
    session.token = {"access_token": "new_access_token", "token_type": "Bearer"}
    print("✅ Token updated via property setter")

    # Clear token
    session.token = None
    print("🗑️  Token cleared")


def oauth2_client_credentials_example():
    """
    Example: OAuth 2.0 Client Credentials flow (server-to-server)
    """
    print("\n=== OAuth 2.0 Client Credentials Flow ===")

    session = OAuth2EnhancedSession(client_id="your_service_client_id")

    try:
        print("🔄 Fetching token using client credentials...")
        token = session.fetch_token(
            "https://api.example.com/oauth/token",
            client_secret="your_service_client_secret",
            grant_type="client_credentials",
            scope=["api:read", "api:write"],
        )
        print("✅ Service token obtained")
        print(f"   Token type: {token.get('token_type', 'N/A')}")
        print(f"   Expires in: {token.get('expires_in', 'N/A')} seconds")

        # Make service-to-service requests
        response = session.get("https://api.example.com/service/data")
        print(f"📊 Service request status: {response.status_code}")

    except Exception as e:
        print(f"❌ Client credentials flow error: {e}")
        print("   This is expected without real service credentials")


def oauth_error_handling_example():
    """
    Example: Robust OAuth error handling
    """
    print("\n=== OAuth Error Handling ===")

    from requests.exceptions import RequestException

    try:
        from oauthlib.oauth2 import TokenExpiredError
        from requests_oauthlib import TokenRequestDenied
    except ImportError:
        print("⚠️  OAuth error classes not available")
        return

    def make_robust_oauth_request(session, url, max_retries=3):
        """Make OAuth request with comprehensive error handling"""
        for attempt in range(max_retries):
            try:
                response = session.get(url)
                response.raise_for_status()
                return response.json()

            except TokenExpiredError:
                print(f"🔄 Token expired on attempt {attempt + 1}, refreshing...")
                # Token will be automatically refreshed if auto_refresh_url is set
                continue

            except TokenRequestDenied as e:
                print(f"❌ Token request denied: {e}")
                raise

            except RequestException as e:
                if attempt == max_retries - 1:
                    print(f"❌ Max retries exceeded: {e}")
                    raise
                print(f"⚠️  Request failed on attempt {attempt + 1}, retrying...")
                continue

        raise Exception("Request failed after all retries")

    # Example usage
    session = OAuth2EnhancedSession(
        client_id="test_client",
        token={"access_token": "test_token", "token_type": "Bearer"},
    )

    try:
        result = make_robust_oauth_request(session, "https://api.example.com/data")
        print("✅ Request successful")
    except Exception as e:
        print(f"❌ Request ultimately failed: {e}")


def oauth_best_practices_example():
    """
    Example: OAuth best practices and security
    """
    print("\n=== OAuth Best Practices ===")

    # 1. Environment-based configuration
    print("1. 🔒 Environment-based configuration:")
    config = {
        "client_id": os.getenv("OAUTH_CLIENT_ID"),
        "client_secret": os.getenv("OAUTH_CLIENT_SECRET"),
        "redirect_uri": os.getenv(
            "OAUTH_REDIRECT_URI", "http://localhost:8080/callback"
        ),
    }

    if not all(config.values()):
        print("   ⚠️  Set OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET environment variables")
    else:
        print("   ✅ Configuration loaded from environment")

    # 2. Secure token storage
    print("2. 💾 Secure token storage:")
    token_dir = Path.home() / ".config" / "myapp"
    token_file = token_dir / "oauth_token.json"

    def secure_save_token(token):
        token_dir.mkdir(parents=True, exist_ok=True)
        with open(token_file, "w") as f:
            json.dump(token, f)
        os.chmod(token_file, 0o600)  # Owner read/write only
        print("   ✅ Token saved with secure permissions")

    # 3. Session reuse and connection pooling
    print("3. 🔄 Session reuse and connection pooling:")

    class OAuthAPIClient:
        def __init__(self, client_id, client_secret):
            self.session = OAuth2EnhancedSession(
                client_id=client_id,
                auto_refresh_url="https://api.example.com/oauth/token",
                auto_refresh_kwargs={"client_secret": client_secret},
                token_updater=secure_save_token,
                # Enhanced features for production
                timeout=(5, 30),  # (connect, read) timeouts
                max_retries=3,
                http_version="2",
            )

            # Load existing token
            if token_file.exists():
                with open(token_file, "r") as f:
                    self.session.token = json.load(f)

        def get_user_data(self):
            return self.session.get("https://api.example.com/user").json()

        def close(self):
            self.session.close()

    print("   ✅ Reusable API client with automatic token management")

    # 4. State parameter for CSRF protection
    print("4. 🛡️  CSRF protection with state parameter:")
    import secrets

    session = OAuth2EnhancedSession(
        client_id="test_client",
        redirect_uri="http://localhost:8080/callback",
        state=secrets.token_urlsafe(32),  # Cryptographically secure random state
    )
    print("   ✅ Secure random state generated for CSRF protection")

    # 5. Scope limitation
    print("5. 🎯 Principle of least privilege - minimal scopes:")
    minimal_scopes = ["user:email"]  # Only request what you need
    session.scope = minimal_scopes
    print(f"   ✅ Limited scopes: {minimal_scopes}")

    print("\n📋 OAuth Security Checklist:")
    print("   ✅ Store credentials in environment variables")
    print("   ✅ Use secure token storage with proper file permissions")
    print("   ✅ Implement automatic token refresh")
    print("   ✅ Use HTTPS for all OAuth endpoints")
    print("   ✅ Validate state parameter to prevent CSRF")
    print("   ✅ Request minimal required scopes")
    print("   ✅ Implement proper error handling")
    print("   ✅ Use connection pooling for performance")


def main():
    """Run all OAuth examples"""
    print("🔐 OAuth Examples for requests-enhanced")
    print("=" * 50)

    if not OAUTH_AVAILABLE:
        print("❌ OAuth functionality not available")
        print("   Install with: pip install requests-enhanced[oauth]")
        return

    print("✅ OAuth functionality available")

    # Run examples
    oauth1_twitter_example()
    oauth2_github_example()
    oauth2_token_management_example()
    oauth2_client_credentials_example()
    oauth_error_handling_example()
    oauth_best_practices_example()

    print("\n🎉 OAuth examples completed!")
    print("\nFor more information:")
    print("   📖 Read the OAuth Usage Guide: docs/oauth-usage-guide.md")
    print(
        "   🔗 requests-enhanced documentation: https://github.com/khollingworth/requests-enhanced"
    )


if __name__ == "__main__":
    main()
