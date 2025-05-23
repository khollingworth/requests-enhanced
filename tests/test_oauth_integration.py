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
        OAuthNotAvailableError
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
    
    @pytest.mark.skipif(not OAUTH_TESTS_ENABLED, reason="OAuth dependencies not available")
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
            client_key='test_client_key',
            client_secret='test_client_secret'
        )
        
        assert session is not None
        assert hasattr(session, 'auth')
        assert session.auth is not None
        assert session._client_key == 'test_client_key'
        assert session._client_secret == 'test_client_secret'
    
    def test_oauth1_session_with_tokens(self):
        """Test OAuth1 session creation with access tokens."""
        session = OAuth1EnhancedSession(
            client_key='test_client_key',
            client_secret='test_client_secret',
            resource_owner_key='test_access_token',
            resource_owner_secret='test_access_secret'
        )
        
        assert session._resource_owner_key == 'test_access_token'
        assert session._resource_owner_secret == 'test_access_secret'
    
    def test_oauth1_session_with_enhanced_features(self):
        """Test OAuth1 session with enhanced session features."""
        session = OAuth1EnhancedSession(
            client_key='test_client_key',
            client_secret='test_client_secret',
            timeout=30,
            max_retries=5,
            http_version='2'
        )
        
        # Should inherit enhanced session capabilities
        assert hasattr(session, 'timeout')
        assert hasattr(session, 'get')  # Basic session method
        assert hasattr(session, 'post')  # Basic session method
    
    @patch('requests_enhanced.oauth._OAuth1Session')
    def test_fetch_request_token(self, mock_oauth1_session):
        """Test fetching OAuth 1.0 request token."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.fetch_request_token.return_value = {
            'oauth_token': 'request_token',
            'oauth_token_secret': 'request_secret'
        }
        mock_oauth1_session.return_value = mock_instance
        
        session = OAuth1EnhancedSession(
            client_key='test_client_key',
            client_secret='test_client_secret'
        )
        
        token = session.fetch_request_token('https://api.example.com/oauth/request_token')
        
        assert token['oauth_token'] == 'request_token'
        assert token['oauth_token_secret'] == 'request_secret'
        assert session._resource_owner_key == 'request_token'
        assert session._resource_owner_secret == 'request_secret'
    
    @patch('requests_enhanced.oauth._OAuth1Session')
    def test_authorization_url(self, mock_oauth1_session):
        """Test generating OAuth 1.0 authorization URL."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.authorization_url.return_value = 'https://api.example.com/oauth/authorize?oauth_token=test'
        mock_oauth1_session.return_value = mock_instance
        
        session = OAuth1EnhancedSession(
            client_key='test_client_key',
            client_secret='test_client_secret'
        )
        
        auth_url = session.authorization_url('https://api.example.com/oauth/authorize')
        
        assert auth_url == 'https://api.example.com/oauth/authorize?oauth_token=test'
    
    @patch('requests_enhanced.oauth._OAuth1Session')
    def test_fetch_access_token(self, mock_oauth1_session):
        """Test fetching OAuth 1.0 access token."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.fetch_access_token.return_value = {
            'oauth_token': 'access_token',
            'oauth_token_secret': 'access_secret'
        }
        mock_oauth1_session.return_value = mock_instance
        
        session = OAuth1EnhancedSession(
            client_key='test_client_key',
            client_secret='test_client_secret'
        )
        
        token = session.fetch_access_token(
            'https://api.example.com/oauth/access_token',
            verifier='test_verifier'
        )
        
        assert token['oauth_token'] == 'access_token'
        assert token['oauth_token_secret'] == 'access_secret'
        assert session._resource_owner_key == 'access_token'
        assert session._resource_owner_secret == 'access_secret'


@pytest.mark.skipif(not OAUTH_TESTS_ENABLED, reason="OAuth dependencies not available")
class TestOAuth2EnhancedSession:
    """Test OAuth 2.0 enhanced session functionality."""
    
    def test_oauth2_session_creation(self):
        """Test basic OAuth2 session creation."""
        session = OAuth2EnhancedSession(
            client_id='test_client_id'
        )
        
        assert session is not None
        assert session._client_id == 'test_client_id'
        assert session.token is None
        assert session.auth is None  # No auth until token is set
    
    def test_oauth2_session_with_token(self):
        """Test OAuth2 session creation with existing token."""
        token = {
            'access_token': 'test_access_token',
            'token_type': 'Bearer',
            'expires_in': 3600
        }
        
        session = OAuth2EnhancedSession(
            client_id='test_client_id',
            token=token
        )
        
        assert session.token == token
        assert session.auth is not None
    
    def test_oauth2_session_with_enhanced_features(self):
        """Test OAuth2 session with enhanced session features."""
        session = OAuth2EnhancedSession(
            client_id='test_client_id',
            timeout=30,
            max_retries=5,
            http_version='3'
        )
        
        # Should inherit enhanced session capabilities
        assert hasattr(session, 'timeout')
        assert hasattr(session, 'get')  # Basic session method
        assert hasattr(session, 'post')  # Basic session method
    
    @patch('requests_enhanced.oauth._OAuth2Session')
    def test_authorization_url(self, mock_oauth2_session):
        """Test generating OAuth 2.0 authorization URL."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.authorization_url.return_value = (
            'https://api.example.com/oauth/authorize?client_id=test&state=random',
            'random_state'
        )
        mock_oauth2_session.return_value = mock_instance
        
        session = OAuth2EnhancedSession(
            client_id='test_client_id'
        )
        
        auth_url, state = session.authorization_url('https://api.example.com/oauth/authorize')
        
        assert 'https://api.example.com/oauth/authorize' in auth_url
        assert state == 'random_state'
        assert session._state == 'random_state'
    
    @patch('requests_enhanced.oauth._OAuth2Session')
    def test_fetch_token(self, mock_oauth2_session):
        """Test fetching OAuth 2.0 access token."""
        # Setup mock
        mock_instance = Mock()
        mock_token = {
            'access_token': 'test_access_token',
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': 'test_refresh_token'
        }
        mock_instance.fetch_token.return_value = mock_token
        mock_oauth2_session.return_value = mock_instance
        
        session = OAuth2EnhancedSession(
            client_id='test_client_id'
        )
        
        token = session.fetch_token(
            'https://api.example.com/oauth/token',
            authorization_response='https://redirect.uri?code=auth_code&state=state'
        )
        
        assert token == mock_token
        assert session.token == mock_token
        assert session.auth is not None
    
    @patch('requests_enhanced.oauth._OAuth2Session')
    def test_refresh_token(self, mock_oauth2_session):
        """Test refreshing OAuth 2.0 access token."""
        # Setup mock
        mock_instance = Mock()
        mock_new_token = {
            'access_token': 'new_access_token',
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': 'new_refresh_token'
        }
        mock_instance.refresh_token.return_value = mock_new_token
        mock_oauth2_session.return_value = mock_instance
        
        # Create session with existing token
        old_token = {
            'access_token': 'old_access_token',
            'refresh_token': 'old_refresh_token'
        }
        session = OAuth2EnhancedSession(
            client_id='test_client_id',
            token=old_token
        )
        
        new_token = session.refresh_token('https://api.example.com/oauth/token')
        
        assert new_token == mock_new_token
        assert session.token == mock_new_token
    
    def test_token_property(self):
        """Test token property getter and setter."""
        session = OAuth2EnhancedSession(client_id='test_client_id')
        
        # Initially no token
        assert session.token is None
        assert session.auth is None
        
        # Set token
        token = {'access_token': 'test_token', 'token_type': 'Bearer'}
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
            client_id='test_client_id',
            token_updater=token_updater
        )
        
        # Simulate token update
        new_token = {'access_token': 'updated_token'}
        session._handle_token_update(new_token)
        
        assert len(updated_tokens) == 1
        assert updated_tokens[0] == new_token
        assert session.token == new_token


@pytest.mark.skipif(not OAUTH_TESTS_ENABLED, reason="OAuth dependencies not available")
class TestOAuthErrorHandling:
    """Test OAuth error handling."""
    
    def test_oauth_not_available_error(self):
        """Test OAuthNotAvailableError exception."""
        error = OAuthNotAvailableError()
        assert "OAuth functionality requires 'requests-oauthlib' package" in str(error)
        
        custom_error = OAuthNotAvailableError("Custom message")
        assert str(custom_error) == "Custom message"
    
    @patch('requests_enhanced.oauth.OAUTH_AVAILABLE', False)
    def test_check_oauth_available_raises_error(self):
        """Test that _check_oauth_available raises error when OAuth not available."""
        with pytest.raises(OAuthNotAvailableError):
            _check_oauth_available()


@pytest.mark.skipif(not OAUTH_TESTS_ENABLED, reason="OAuth dependencies not available")
class TestOAuthIntegrationWithHTTPVersions:
    """Test OAuth integration with different HTTP versions."""
    
    def test_oauth1_with_http2(self):
        """Test OAuth1 session with HTTP/2."""
        session = OAuth1EnhancedSession(
            client_key='test_key',
            client_secret='test_secret',
            http_version='2'
        )
        
        assert hasattr(session, 'http_version')
        # The actual HTTP version setting depends on the Session implementation
    
    def test_oauth2_with_http3(self):
        """Test OAuth2 session with HTTP/3."""
        session = OAuth2EnhancedSession(
            client_id='test_client_id',
            http_version='3'
        )
        
        assert hasattr(session, 'http_version')
        # The actual HTTP version setting depends on the Session implementation
    
    def test_oauth_with_retry_configuration(self):
        """Test OAuth sessions with retry configuration."""
        oauth1_session = OAuth1EnhancedSession(
            client_key='test_key',
            client_secret='test_secret',
            max_retries=3,
            timeout=30
        )
        
        oauth2_session = OAuth2EnhancedSession(
            client_id='test_client_id',
            max_retries=5,
            timeout=45
        )
        
        # Both should inherit retry capabilities from enhanced Session
        assert hasattr(oauth1_session, 'get')
        assert hasattr(oauth2_session, 'post')


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
            OAUTH_AVAILABLE as available
        )
        
        assert available is False
        assert OAuth1 is None
        assert OAuth2 is None
