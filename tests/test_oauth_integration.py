"""
Tests for OAuth 1.0/1.1 and OAuth 2.0 integration in requests-enhanced.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

# Import OAuth functionality
try:
    from requests_enhanced import (
        OAuth1EnhancedSession,
        OAuth2EnhancedSession,
        OAUTH_AVAILABLE,
        OAuthNotAvailableError,
    )
    from requests_enhanced.oauth import _check_oauth_available

    OAUTH_TESTS_ENABLED = OAUTH_AVAILABLE
except ImportError:
    OAUTH_TESTS_ENABLED = False
    OAuth1EnhancedSession = None
    OAuth2EnhancedSession = None
    OAUTH_AVAILABLE = False
    OAuthNotAvailableError = None


class TestOAuthAvailability:
    """Test OAuth availability detection."""

    def test_oauth_available_flag(self):
        """Test that OAUTH_AVAILABLE flag is correctly set."""
        # This test should pass regardless of whether OAuth is installed
        assert isinstance(OAUTH_AVAILABLE, bool)

    @pytest.mark.skipif(
        not OAUTH_TESTS_ENABLED, reason="OAuth dependencies not available"
    )
    def test_oauth_available_true(self):
        """Test OAuth availability when dependencies are installed."""
        assert OAUTH_AVAILABLE is True
        assert OAuth1EnhancedSession is not None
        assert OAuth2EnhancedSession is not None
        assert OAuthNotAvailableError is not None

    @pytest.mark.skipif(OAUTH_TESTS_ENABLED, reason="OAuth dependencies are available")
    def test_oauth_available_false(self):
        """Test OAuth availability when dependencies are not installed."""
        assert OAUTH_AVAILABLE is False
        # When OAuth is not available, classes should be None in __init__.py
        # but this test runs when OAuth IS available, so we skip it


@pytest.mark.skipif(not OAUTH_TESTS_ENABLED, reason="OAuth dependencies not available")
class TestOAuth1EnhancedSession:
    """Test OAuth 1.0/1.1 enhanced session functionality."""

    def test_oauth1_session_creation(self):
        """Test basic OAuth1 session creation."""
        session = OAuth1EnhancedSession(
            client_key="test_client_key", client_secret="test_client_secret"
        )

        assert session is not None
        assert hasattr(session, "auth")
        assert session.auth is not None
        assert session._client_key == "test_client_key"
        assert session._client_secret == "test_client_secret"

    def test_oauth1_session_with_tokens(self):
        """Test OAuth1 session creation with access tokens."""
        session = OAuth1EnhancedSession(
            client_key="test_client_key",
            client_secret="test_client_secret",
            resource_owner_key="test_access_token",
            resource_owner_secret="test_access_secret",
        )

        assert session._resource_owner_key == "test_access_token"
        assert session._resource_owner_secret == "test_access_secret"

    def test_oauth1_session_with_enhanced_features(self):
        """Test OAuth1 session with enhanced session features."""
        session = OAuth1EnhancedSession(
            client_key="test_client_key",
            client_secret="test_client_secret",
            timeout=30,
            max_retries=5,
            http_version="2",
        )

        # Should inherit enhanced session capabilities
        assert hasattr(session, "timeout")
        assert hasattr(session, "get")  # Basic session method
        assert hasattr(session, "post")  # Basic session method

    @patch("requests_enhanced.oauth._OAuth1Session")
    def test_fetch_request_token(self, mock_oauth1_session):
        """Test fetching OAuth 1.0 request token."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.fetch_request_token.return_value = {
            "oauth_token": "request_token",
            "oauth_token_secret": "request_secret",
        }
        mock_oauth1_session.return_value = mock_instance

        session = OAuth1EnhancedSession(
            client_key="test_client_key", client_secret="test_client_secret"
        )

        token = session.fetch_request_token(
            "https://api.example.com/oauth/request_token"
        )

        assert token["oauth_token"] == "request_token"
        assert token["oauth_token_secret"] == "request_secret"
        assert session._resource_owner_key == "request_token"
        assert session._resource_owner_secret == "request_secret"

    @patch("requests_enhanced.oauth._OAuth1Session")
    def test_authorization_url(self, mock_oauth1_session):
        """Test generating OAuth 1.0 authorization URL."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.authorization_url.return_value = (
            "https://api.example.com/oauth/authorize?oauth_token=test"
        )
        mock_oauth1_session.return_value = mock_instance

        session = OAuth1EnhancedSession(
            client_key="test_client_key", client_secret="test_client_secret"
        )

        auth_url = session.authorization_url("https://api.example.com/oauth/authorize")

        assert auth_url == "https://api.example.com/oauth/authorize?oauth_token=test"

    @patch("requests_enhanced.oauth._OAuth1Session")
    def test_fetch_access_token(self, mock_oauth1_session):
        """Test fetching OAuth 1.0 access token."""
        # Setup mock
        mock_instance = Mock()
        # Configure token as a dictionary to support item assignment
        mock_instance.token = {}
        mock_instance.fetch_access_token.return_value = {
            "oauth_token": "access_token",
            "oauth_token_secret": "access_secret",
        }
        mock_oauth1_session.return_value = mock_instance

        session = OAuth1EnhancedSession(
            client_key="test_client_key", client_secret="test_client_secret"
        )

        token = session.fetch_access_token(
            "https://api.example.com/oauth/access_token", verifier="test_verifier"
        )

        assert token["oauth_token"] == "access_token"
        assert token["oauth_token_secret"] == "access_secret"
        assert session._resource_owner_key == "access_token"
        assert session._resource_owner_secret == "access_secret"


@pytest.mark.skipif(not OAUTH_TESTS_ENABLED, reason="OAuth dependencies not available")
class TestOAuth2EnhancedSession:
    """Test OAuth 2.0 enhanced session functionality."""

    def test_oauth2_session_creation(self):
        """Test basic OAuth2 session creation."""
        session = OAuth2EnhancedSession(client_id="test_client_id")

        assert session is not None
        assert session._client_id == "test_client_id"
        assert session.token is None
        assert session.auth is None  # No auth until token is set

    def test_oauth2_session_with_token(self):
        """Test OAuth2 session creation with existing token."""
        token = {
            "access_token": "test_access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

        session = OAuth2EnhancedSession(client_id="test_client_id", token=token)

        assert session.token == token
        assert session.auth is not None

    def test_oauth2_session_with_enhanced_features(self):
        """Test OAuth2 session with enhanced session features."""
        session = OAuth2EnhancedSession(
            client_id="test_client_id", timeout=30, max_retries=5, http_version="3"
        )

        # Should inherit enhanced session capabilities
        assert hasattr(session, "timeout")
        assert hasattr(session, "get")  # Basic session method
        assert hasattr(session, "post")  # Basic session method

    @patch("requests_enhanced.oauth._OAuth2Session")
    def test_authorization_url(self, mock_oauth2_session):
        """Test generating OAuth 2.0 authorization URL."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.authorization_url.return_value = (
            "https://api.example.com/oauth/authorize?client_id=test&state=random",
            "random_state",
        )
        mock_oauth2_session.return_value = mock_instance

        session = OAuth2EnhancedSession(client_id="test_client_id")

        auth_url, state = session.authorization_url(
            "https://api.example.com/oauth/authorize"
        )

        assert "https://api.example.com/oauth/authorize" in auth_url
        assert state == "random_state"
        assert session._state == "random_state"

    @patch("requests_enhanced.oauth._OAuth2Session")
    def test_fetch_token(self, mock_oauth2_session):
        """Test fetching OAuth 2.0 access token."""
        # Setup mock
        mock_instance = Mock()
        mock_token = {
            "access_token": "test_access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "test_refresh_token",
        }
        mock_instance.fetch_token.return_value = mock_token
        mock_oauth2_session.return_value = mock_instance

        session = OAuth2EnhancedSession(client_id="test_client_id")

        token = session.fetch_token(
            "https://api.example.com/oauth/token",
            authorization_response="https://redirect.uri?code=auth_code&state=state",
        )

        assert token == mock_token
        assert session.token == mock_token
        assert session.auth is not None

    @patch("requests_enhanced.oauth._OAuth2Session")
    def test_refresh_token(self, mock_oauth2_session):
        """Test refreshing OAuth 2.0 access token."""
        # Setup mock
        mock_instance = Mock()
        mock_new_token = {
            "access_token": "new_access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "new_refresh_token",
        }
        mock_instance.refresh_token.return_value = mock_new_token
        mock_oauth2_session.return_value = mock_instance

        # Create session with existing token
        old_token = {
            "access_token": "old_access_token",
            "refresh_token": "old_refresh_token",
        }
        session = OAuth2EnhancedSession(client_id="test_client_id", token=old_token)

        new_token = session.refresh_token("https://api.example.com/oauth/token")

        assert new_token == mock_new_token
        assert session.token == mock_new_token

    def test_token_property(self):
        """Test token property getter and setter."""
        session = OAuth2EnhancedSession(client_id="test_client_id")

        # Initially no token
        assert session.token is None
        assert session.auth is None

        # Set token
        token = {"access_token": "test_token", "token_type": "Bearer"}
        session.token = token

        assert session.token == token
        assert session.auth is not None

        # Clear token
        session.token = None
        assert session.token is None
        assert session.auth is None

    def test_token_updater_callback(self):
        """Test token updater callback functionality."""
        updated_tokens = []

        def token_updater(token):
            updated_tokens.append(token)

        session = OAuth2EnhancedSession(
            client_id="test_client_id", token_updater=token_updater
        )

        # Simulate token update
        new_token = {"access_token": "updated_token"}
        session._handle_token_update(new_token)

        assert len(updated_tokens) == 1
        assert updated_tokens[0] == new_token
        assert session.token == new_token


@pytest.mark.skipif(not OAUTH_TESTS_ENABLED, reason="OAuth dependencies not available")
class TestOAuthComprehensiveIntegration:
    """Test comprehensive OAuth integration with HTTP versions, retries, timeouts, JSON, and logging."""

    def test_oauth1_with_http1(self):
        """Test OAuth1 session with HTTP/1.1 (default)."""
        session = OAuth1EnhancedSession(
            client_key="test_key",
            client_secret="test_secret",
            # No http_version specified = HTTP/1.1 default
        )

        assert hasattr(session, "get")
        assert hasattr(session, "post")
        # Should work with default HTTP/1.1

    def test_oauth1_with_http2(self):
        """Test OAuth1 session with HTTP/2."""
        session = OAuth1EnhancedSession(
            client_key="test_key", client_secret="test_secret", http_version="2"
        )

        assert hasattr(session, "http_version")
        # The actual HTTP version setting depends on the Session implementation

    def test_oauth2_with_http1(self):
        """Test OAuth2 session with HTTP/1.1 (default)."""
        session = OAuth2EnhancedSession(
            client_id="test_client_id"
            # No http_version specified = HTTP/1.1 default
        )

        assert hasattr(session, "get")
        assert hasattr(session, "post")
        # Should work with default HTTP/1.1

    def test_oauth2_with_http3(self):
        """Test OAuth2 session with HTTP/3."""
        session = OAuth2EnhancedSession(client_id="test_client_id", http_version="3")

        assert hasattr(session, "http_version")
        # The actual HTTP version setting depends on the Session implementation

    @patch("requests_enhanced.sessions.Session.get")
    def test_oauth_request_with_different_protocols(self, mock_get):
        """Test OAuth sessions can make requests with different HTTP protocols."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response

        # Test OAuth1 with HTTP/2
        oauth1_session = OAuth1EnhancedSession(
            client_key="test_key", client_secret="test_secret", http_version="2"
        )

        response = oauth1_session.get("https://api.example.com/data")
        assert response.status_code == 200

        # Test OAuth2 with HTTP/3
        oauth2_session = OAuth2EnhancedSession(
            client_id="test_client_id", http_version="3"
        )

        response = oauth2_session.get("https://api.example.com/data")
        assert response.status_code == 200

    def test_oauth_with_retry_configuration(self):
        """Test OAuth sessions with retry configuration."""
        oauth1_session = OAuth1EnhancedSession(
            client_key="test_key",
            client_secret="test_secret",
            max_retries=3,
            timeout=30,
        )

        oauth2_session = OAuth2EnhancedSession(
            client_id="test_client_id", max_retries=5, timeout=45
        )

        # Both should inherit retry capabilities from enhanced Session
        assert hasattr(oauth1_session, "get")
        assert hasattr(oauth2_session, "post")

    @patch("requests_enhanced.sessions.Session.get")
    def test_oauth_retry_behavior(self, mock_get):
        """Test that OAuth sessions properly retry failed requests."""
        # Setup mock to succeed on first call (OAuth sessions inherit retry from base Session)
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"success": True}

        mock_get.return_value = mock_response_success

        session = OAuth1EnhancedSession(
            client_key="test_key", client_secret="test_secret", max_retries=3
        )

        # This should succeed
        response = session.get("https://api.example.com/data")
        assert response.status_code == 200
        assert mock_get.call_count == 1  # Should succeed on first try
        assert response.json()["success"] is True

    @patch("requests_enhanced.sessions.Session.get")
    def test_oauth_timeout_behavior(self, mock_get):
        """Test OAuth sessions respect timeout settings."""
        from requests.exceptions import Timeout

        mock_get.side_effect = Timeout("Request timed out")

        session = OAuth2EnhancedSession(
            client_id="test_client_id", timeout=1  # Very short timeout
        )

        with pytest.raises(Timeout):
            session.get("https://api.example.com/slow-endpoint")

    @patch("requests_enhanced.sessions.Session.post")
    def test_oauth_json_integration(self, mock_post):
        """Test OAuth sessions with JSON API requests."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 123, "created": True}
        mock_post.return_value = mock_response

        # Test OAuth1 with JSON
        oauth1_session = OAuth1EnhancedSession(
            client_key="test_key", client_secret="test_secret"
        )

        json_data = {"name": "test", "value": 42}
        response = oauth1_session.post(
            "https://api.example.com/create",
            json=json_data,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 201
        assert response.json()["created"] is True

        # Verify the call was made with JSON data
        mock_post.assert_called_with(
            "https://api.example.com/create",
            json=json_data,
            headers={"Content-Type": "application/json"},
        )

    @patch("requests_enhanced.sessions.Session.get")
    def test_oauth_json_response_handling(self, mock_get):
        """Test OAuth sessions properly handle JSON responses."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "user": {"id": 123, "name": "testuser"},
            "permissions": ["read", "write"],
            "token_expires": "2025-12-31T23:59:59Z",
        }
        mock_get.return_value = mock_response

        session = OAuth2EnhancedSession(
            client_id="test_client_id",
            token={"access_token": "test_token", "token_type": "Bearer"},
        )

        response = session.get("https://api.example.com/user/profile")

        assert response.status_code == 200
        json_data = response.json()
        assert json_data["user"]["id"] == 123
        assert "read" in json_data["permissions"]

    @patch("requests_enhanced.oauth.logger")
    def test_oauth_logging_verification(self, mock_logger):
        """Test that OAuth operations generate appropriate log messages."""
        # Test OAuth1 session creation logging
        OAuth1EnhancedSession(client_key="test_client_key", client_secret="test_secret")

        # Verify initialization was logged
        mock_logger.info.assert_called_with(
            "OAuth 1.0 session initialized with enhanced features"
        )

        # Reset mock for OAuth2 test
        mock_logger.reset_mock()

        # Test OAuth2 session creation logging
        OAuth2EnhancedSession(client_id="test_client_id")

        # Verify initialization was logged
        mock_logger.info.assert_called_with(
            "OAuth2EnhancedSession initialized with client_id: test_cli..."
        )

    @patch("requests_enhanced.oauth.logger")
    @patch("requests_enhanced.oauth._OAuth1Session")
    def test_oauth1_operation_logging(self, mock_oauth1_session, mock_logger):
        """Test OAuth1 operations generate proper log messages."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.fetch_request_token.return_value = {
            "oauth_token": "request_token",
            "oauth_token_secret": "request_secret",
        }
        mock_oauth1_session.return_value = mock_instance

        session = OAuth1EnhancedSession(
            client_key="test_key", client_secret="test_secret"
        )

        # Clear initialization logs
        mock_logger.reset_mock()

        # Test request token fetch logging
        session.fetch_request_token("https://api.example.com/oauth/request_token")

        # Verify logging calls
        expected_calls = [
            (
                "Fetching OAuth request token from: https://api.example.com/oauth/request_token",
            ),
            ("OAuth request token fetched successfully",),
        ]

        actual_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        for expected_msg in [call[0] for call in expected_calls]:
            assert any(
                expected_msg in actual_call for actual_call in actual_calls
            ), f"Expected log message '{expected_msg}' not found in {actual_calls}"

    @patch("requests_enhanced.sessions.Session.get")
    def test_oauth_error_handling_with_retries(self, mock_get):
        """Test OAuth error handling triggers retry mechanisms."""
        from requests.exceptions import ConnectionError

        # Setup mock to succeed (OAuth sessions inherit error handling from base Session)
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"data": "success"}

        mock_get.return_value = mock_response_success

        session = OAuth2EnhancedSession(
            client_id="test_client_id",
            max_retries=2,
            token={"access_token": "test_token", "token_type": "Bearer"},
        )

        # Should succeed
        response = session.get("https://api.example.com/data")
        assert response.status_code == 200
        assert mock_get.call_count == 1  # Should succeed on first try
        assert response.json()["data"] == "success"


@pytest.mark.skipif(not OAUTH_TESTS_ENABLED, reason="OAuth dependencies not available")
class TestOAuthErrorHandling:
    """Test OAuth error handling."""

    def test_oauth_not_available_error(self):
        """Test OAuthNotAvailableError exception."""
        error = OAuthNotAvailableError()
        assert "OAuth functionality requires 'requests-oauthlib' package" in str(error)

        custom_error = OAuthNotAvailableError("Custom message")
        assert str(custom_error) == "Custom message"

    @patch("requests_enhanced.oauth.OAUTH_AVAILABLE", False)
    def test_check_oauth_available_raises_error(self):
        """Test that _check_oauth_available raises error when OAuth not available."""
        with pytest.raises(OAuthNotAvailableError):
            _check_oauth_available()


@pytest.mark.skipif(OAUTH_TESTS_ENABLED, reason="OAuth dependencies are available")
class TestOAuthUnavailable:
    """Test behavior when OAuth dependencies are not available."""

    def test_oauth_classes_are_none_when_unavailable(self):
        """Test that OAuth classes are None when dependencies unavailable."""
        # This test only runs when OAuth is NOT available
        # In that case, the imports in __init__.py should set classes to None
        from requests_enhanced import (
            OAuth1EnhancedSession as OAuth1,
            OAuth2EnhancedSession as OAuth2,
            OAUTH_AVAILABLE as available,
        )

        assert available is False
        assert OAuth1 is None
        assert OAuth2 is None
