"""
OAuth 1.0/1.1 and OAuth 2.0 authentication support for requests-enhanced.

This module provides OAuth authentication capabilities that integrate seamlessly
with the enhanced Session class, supporting HTTP/2, HTTP/3, retry mechanisms,
and enhanced logging.
"""

from typing import Any, Dict, Optional, Tuple, Union, Callable
import logging

# Check for OAuth dependencies
try:
    from requests_oauthlib import OAuth1Session as _OAuth1Session
    from requests_oauthlib import OAuth2Session as _OAuth2Session
    from requests_oauthlib import OAuth1, OAuth2
    from oauthlib.oauth1 import SIGNATURE_HMAC, SIGNATURE_RSA, SIGNATURE_PLAINTEXT
    from oauthlib.oauth2 import WebApplicationClient, MobileApplicationClient

    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False
    # Create stub classes for type hints
    _OAuth1Session = object  # type: ignore
    _OAuth2Session = object  # type: ignore
    OAuth1 = object  # type: ignore
    OAuth2 = object  # type: ignore
    # Define fallback constants
    SIGNATURE_HMAC = "HMAC-SHA1"  # type: ignore
    SIGNATURE_RSA = "RSA-SHA1"  # type: ignore
    SIGNATURE_PLAINTEXT = "PLAINTEXT"  # type: ignore
    WebApplicationClient = object  # type: ignore
    MobileApplicationClient = object  # type: ignore

from .sessions import Session
from .exceptions import RequestsEnhancedError

logger = logging.getLogger(__name__)


class OAuthNotAvailableError(RequestsEnhancedError):
    """
    Raised when OAuth functionality is requested but dependencies are not
    available.

    OAuth functionality requires 'requests-oauthlib' package. Install with:
    pip install requests-enhanced[oauth]
    """

    def __init__(
        self,
        message: str = (
            "OAuth functionality requires 'requests-oauthlib' package. "
            "Install with: pip install requests-enhanced[oauth]"
        ),
    ):
        super().__init__(message)


def _check_oauth_available() -> None:
    """Check if OAuth dependencies are available and raise error if not."""
    if not OAUTH_AVAILABLE:
        raise OAuthNotAvailableError()


if OAUTH_AVAILABLE:

    class OAuth1EnhancedSession(Session):
        """
        Enhanced Session with OAuth 1.0/1.1 authentication support.

        Combines the OAuth 1.0/1.1 capabilities of requests-oauthlib with the
        enhanced features of requests-enhanced including HTTP/2, HTTP/3, retry
        mechanisms, and enhanced logging.

        Args:
            client_key: OAuth client key (consumer key)
            client_secret: OAuth client secret (consumer secret)
            resource_owner_key: OAuth resource owner key (access token)
            resource_owner_secret: OAuth resource owner secret (access token secret)
            callback_uri: OAuth callback URI
            signature_method: OAuth signature method (HMAC-SHA1, RSA-SHA1, PLAINTEXT)
            signature_type: Where to place OAuth signature (auth_header, query, body)
            rsa_key: RSA key for RSA-SHA1 signature method
            verifier: OAuth verifier for completing authorization
            client_class: OAuth client class to use
            force_include_body: Force inclusion of body in signature
            **kwargs: Additional arguments passed to Session

        Example:
            >>> session = OAuth1EnhancedSession(
            ...     client_key='your_client_key',
            ...     client_secret='your_client_secret',
            ...     http_version='2'  # Use HTTP/2
            ... )
            >>> # Complete OAuth 1.0 workflow
            >>> session.fetch_request_token(
            ...     'https://api.example.com/oauth/request_token'
            ... )
            >>> auth_url = session.authorization_url(
            ...     'https://api.example.com/oauth/authorize'
            ... )
            >>> # User authorizes...
            >>> session.fetch_access_token(
            ...     'https://api.example.com/oauth/access_token',
            ...     verifier='user_verifier'
            ... )
            >>> # Make authenticated requests
            >>> response = session.get('https://api.example.com/protected')
        """

        def __init__(
            self,
            client_key: str,
            client_secret: Optional[str] = None,
            resource_owner_key: Optional[str] = None,
            resource_owner_secret: Optional[str] = None,
            callback_uri: Optional[str] = None,
            signature_method: str = SIGNATURE_HMAC,
            signature_type: str = "auth_header",
            rsa_key: Optional[str] = None,
            verifier: Optional[str] = None,
            client_class: Optional[Any] = None,
            force_include_body: bool = False,
            **kwargs: Any,
        ) -> None:
            _check_oauth_available()

            # Initialize the enhanced Session first
            # (only with Session-compatible kwargs)
            super().__init__(**kwargs)

            # Store OAuth parameters
            self._client_key = client_key
            self._client_secret = client_secret
            self._resource_owner_key = resource_owner_key
            self._resource_owner_secret = resource_owner_secret
            self._callback_uri = callback_uri
            self._signature_method = signature_method
            self._signature_type = signature_type
            self._rsa_key = rsa_key
            self._verifier = verifier
            self._client_class = client_class
            self._force_include_body = force_include_body

            # Create the OAuth1Session for OAuth operations
            self._oauth_session = _OAuth1Session(
                client_key=client_key,
                client_secret=client_secret,
                resource_owner_key=resource_owner_key,
                resource_owner_secret=resource_owner_secret,
                callback_uri=callback_uri,
                signature_method=signature_method,
                signature_type=signature_type,
                rsa_key=rsa_key,
                verifier=verifier,
                client_class=client_class,
                force_include_body=force_include_body,
            )

            # Set up OAuth authentication for all requests
            self.auth = OAuth1(
                client_key=client_key,
                client_secret=client_secret,
                resource_owner_key=resource_owner_key,
                resource_owner_secret=resource_owner_secret,
                signature_method=signature_method,
                signature_type=signature_type,
                rsa_key=rsa_key,
                verifier=verifier,
            )

            logger.info("OAuth 1.0 session initialized with enhanced features")

        def fetch_request_token(
            self,
            request_token_url: str,
            realm: Optional[str] = None,
            **request_kwargs: Any,
        ) -> Dict[str, str]:
            """
            Fetch an OAuth request token from the given URL.

            Args:
                request_token_url: URL to fetch request token from
                realm: OAuth realm parameter
                **request_kwargs: Additional arguments for the request

            Returns:
                Dict containing oauth_token and oauth_token_secret

            Raises:
                OAuthNotAvailableError: If OAuth dependencies are not installed
            """
            _check_oauth_available()

            logger.info(f"Fetching OAuth request token from: {request_token_url}")

            # Use the OAuth session for this operation
            token = self._oauth_session.fetch_request_token(
                request_token_url, realm=realm, **request_kwargs
            )

            # Update our auth with the new token
            self._resource_owner_key = token["oauth_token"]
            self._resource_owner_secret = token["oauth_token_secret"]

            # Update the auth object
            self.auth = OAuth1(
                client_key=self._client_key,
                client_secret=self._client_secret,
                resource_owner_key=self._resource_owner_key,
                resource_owner_secret=self._resource_owner_secret,
                signature_method=self._signature_method,
                signature_type=self._signature_type,
                rsa_key=self._rsa_key,
                verifier=self._verifier,
            )

            logger.info("OAuth request token fetched successfully")
            return token

        def authorization_url(
            self, authorization_url: str, **request_kwargs: Any
        ) -> str:
            """
            Get the authorization URL for the user to visit.

            Args:
                authorization_url: Base authorization URL
                **request_kwargs: Additional query parameters

            Returns:
                Complete authorization URL for user to visit
            """
            _check_oauth_available()

            logger.info(f"Generating authorization URL from: {authorization_url}")

            auth_url = self._oauth_session.authorization_url(
                authorization_url, **request_kwargs
            )

            logger.info("Authorization URL generated successfully")
            return auth_url

        def fetch_access_token(
            self,
            access_token_url: str,
            verifier: Optional[str] = None,
            **request_kwargs: Any,
        ) -> Dict[str, str]:
            """
            Fetch an OAuth access token from the given URL.

            Args:
                access_token_url: URL to fetch access token from
                verifier: OAuth verifier from authorization callback
                **request_kwargs: Additional arguments for the request

            Returns:
                Dict containing oauth_token and oauth_token_secret
            """
            _check_oauth_available()

            logger.info(f"Fetching OAuth access token from: {access_token_url}")

            if verifier:
                self._oauth_session.token["oauth_verifier"] = verifier  # type: ignore

            # Fetch the access token
            token = self._oauth_session.fetch_access_token(
                access_token_url, verifier=verifier, **request_kwargs
            )

            # Update our credentials
            self._resource_owner_key = token["oauth_token"]
            self._resource_owner_secret = token["oauth_token_secret"]

            # Update the auth object with access token
            self.auth = OAuth1(
                client_key=self._client_key,
                client_secret=self._client_secret,
                resource_owner_key=self._resource_owner_key,
                resource_owner_secret=self._resource_owner_secret,
                signature_method=self._signature_method,
                signature_type=self._signature_type,
                rsa_key=self._rsa_key,
                verifier=self._verifier,
            )

            logger.info("OAuth access token fetched successfully")
            return token

    class OAuth2EnhancedSession(Session):
        """
        Enhanced Session with OAuth 2.0 authentication support.

        Combines the OAuth 2.0 capabilities of requests-oauthlib with the
        enhanced features of requests-enhanced including HTTP/2, HTTP/3, retry
        mechanisms, and enhanced logging.

        Args:
            client_id: OAuth 2.0 client ID
            redirect_uri: OAuth 2.0 redirect URI
            token: Current OAuth 2.0 token dict
            state: OAuth 2.0 state parameter
            state_generator: Function to generate state parameter
            token_updater: Callback function to save updated tokens
            auto_refresh_url: URL for automatic token refresh
            auto_refresh_kwargs: Additional kwargs for token refresh
            scope: OAuth 2.0 scope list or string
            **kwargs: Additional arguments passed to Session

        Example:
            >>> session = OAuth2EnhancedSession(
            ...     client_id='your_client_id',
            ...     redirect_uri='https://your-app.com/callback',
            ...     scope=['read', 'write'],
            ...     http_version='3'  # Use HTTP/3
            ... )
            >>> # OAuth 2.0 Authorization Code flow
            >>> authorization_url, state = session.authorization_url(
            ...     'https://api.example.com/oauth/authorize'
            ... )
            >>> # User authorizes and returns with code...
            >>> token = session.fetch_token(
            ...     'https://api.example.com/oauth/token',
            ...     authorization_response=callback_url,
            ...     client_secret='your_client_secret'
            ... )
            >>> # Make authenticated requests with automatic token refresh
            >>> response = session.get('https://api.example.com/protected')
        """

        def __init__(
            self,
            client_id: str,
            redirect_uri: Optional[str] = None,
            token: Optional[Dict[str, Any]] = None,
            state: Optional[str] = None,
            state_generator: Optional[Callable[[], str]] = None,
            token_updater: Optional[Callable[[Dict[str, Any]], None]] = None,
            auto_refresh_url: Optional[str] = None,
            auto_refresh_kwargs: Optional[Dict[str, Any]] = None,
            scope: Optional[Union[str, list]] = None,
            **kwargs: Any,
        ) -> None:
            _check_oauth_available()

            # Store OAuth parameters
            self._client_id = client_id
            self._redirect_uri = redirect_uri
            self._token = token
            self._state = state
            self._state_generator = state_generator
            self._token_updater = token_updater
            self._auto_refresh_url = auto_refresh_url
            self._auto_refresh_kwargs = auto_refresh_kwargs or {}
            self._scope = scope

            # Initialize the enhanced Session first
            # (only with Session-compatible kwargs)
            super().__init__(**kwargs)

            # Create the OAuth2Session for OAuth operations
            self._oauth_session = _OAuth2Session(
                client_id=client_id,
                redirect_uri=redirect_uri,
                token=token,
                state=state,
                scope=scope,
                auto_refresh_url=auto_refresh_url,
                auto_refresh_kwargs=auto_refresh_kwargs,
                token_updater=self._handle_token_update,
            )

            # Set up OAuth authentication if we have a token
            if token:
                self.auth = OAuth2(client_id=client_id, token=token)

            logger.info(
                f"OAuth2EnhancedSession initialized with client_id: {client_id[:8]}..."
            )

        def _handle_token_update(self, token: Dict[str, Any]) -> None:
            """Handle token updates from automatic refresh."""
            self._token = token
            self.auth = OAuth2(client_id=self._client_id, token=token)

            if self._token_updater:
                self._token_updater(token)

            logger.info("OAuth 2.0 token updated successfully")

        def authorization_url(
            self, authorization_url: str, state: Optional[str] = None, **kwargs: Any
        ) -> Tuple[str, Optional[str]]:
            """
            Generate an authorization URL.

            Args:
                authorization_url: Base authorization URL
                state: OAuth 2.0 state parameter
                **kwargs: Additional query parameters

            Returns:
                Tuple of (authorization_url, state)
            """
            _check_oauth_available()

            logger.info(
                f"Generating OAuth 2.0 authorization URL from: {authorization_url}"
            )

            auth_url, state = self._oauth_session.authorization_url(
                authorization_url, state=state, **kwargs
            )

            self._state = state
            logger.info("OAuth 2.0 authorization URL generated successfully")
            return auth_url, state

        def fetch_token(
            self,
            token_url: str,
            code: Optional[str] = None,
            authorization_response: Optional[str] = None,
            body: str = "",
            auth: Optional[Any] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            method: str = "POST",
            timeout: Optional[float] = None,
            headers: Optional[Dict[str, str]] = None,
            verify: Union[bool, str] = True,
            proxies: Optional[Dict[str, str]] = None,
            include_client_id: bool = False,
            **kwargs: Any,
        ) -> Dict[str, Any]:
            """
            Fetch an OAuth 2.0 access token.

            Args:
                token_url: URL to fetch the token from
                code: Authorization code
                authorization_response: Authorization response URL
                body: Request body
                auth: Authentication tuple or object
                username: Username for password grant
                password: Password for password grant
                method: HTTP method
                timeout: Request timeout
                headers: Request headers
                verify: SSL verification (bool only for OAuth2Session compatibility)
                proxies: Request proxies
                include_client_id: Whether to include client ID
                **kwargs: Additional arguments

            Returns:
                Token dictionary
            """
            _check_oauth_available()

            logger.info(f"Fetching OAuth 2.0 token from: {token_url}")

            # Convert verify to bool for OAuth2Session compatibility
            verify_bool = verify if isinstance(verify, bool) else True

            token = self._oauth_session.fetch_token(
                token_url=token_url,
                code=code,
                authorization_response=authorization_response,
                body=body,
                auth=auth,
                username=username,
                password=password,
                method=method,
                timeout=timeout,
                headers=headers,
                verify=verify_bool,
                proxies=proxies,
                include_client_id=include_client_id,
                **kwargs,
            )

            # Update our token and auth
            self._token = token
            self.auth = OAuth2(client_id=self._client_id, token=token)

            logger.info("OAuth 2.0 token fetched successfully")
            return token

        def refresh_token(
            self,
            token_url: str,
            refresh_token: Optional[str] = None,
            body: str = "",
            auth: Optional[tuple] = None,
            timeout: Optional[float] = None,
            headers: Optional[Dict[str, str]] = None,
            verify: Union[bool, str] = True,
            **kwargs: Any,
        ) -> Dict[str, Any]:
            """
            Refresh an OAuth 2.0 access token.

            Args:
                token_url: URL to refresh token from
                refresh_token: Refresh token to use
                body: Request body
                auth: HTTP Basic authentication tuple
                timeout: Request timeout
                headers: Request headers
                verify: SSL verification
                **kwargs: Additional arguments

            Returns:
                New token dictionary
            """
            _check_oauth_available()

            logger.info(f"Refreshing OAuth 2.0 token from: {token_url}")

            # Convert verify to bool for OAuth2Session compatibility
            verify_bool = verify if isinstance(verify, bool) else True

            # Use current refresh token if not provided
            if refresh_token is None and self._token:
                refresh_token = self._token.get("refresh_token")

            # Refresh the token
            token = self._oauth_session.refresh_token(
                token_url=token_url,
                refresh_token=refresh_token,
                body=body,
                auth=auth,
                timeout=timeout,
                headers=headers,
                verify=verify_bool,
                **kwargs,
            )

            # Update our token and auth
            self._token = token
            self.auth = OAuth2(client_id=self._client_id, token=token)

            logger.info("OAuth 2.0 token refreshed successfully")
            return token

        @property
        def token(self) -> Optional[Dict[str, Any]]:
            """Get the current OAuth 2.0 token."""
            return self._token

        @token.setter
        def token(self, value: Optional[Dict[str, Any]]) -> None:
            """Set the OAuth 2.0 token."""
            self._token = value
            if value:
                self.auth = OAuth2(client_id=self._client_id, token=value)
            else:
                self.auth = None

else:
    # When OAuth dependencies are not available, create placeholder classes
    # that raise an error when OAuth is not available
    class OAuth1EnhancedSession:  # type: ignore
        """
        Placeholder OAuth1 session that raises an error when OAuth is not
        available.
        """

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise OAuthNotAvailableError()

    class OAuth2EnhancedSession:  # type: ignore
        """
        Placeholder OAuth2 session that raises an error when OAuth is not
        available.
        """

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise OAuthNotAvailableError()
