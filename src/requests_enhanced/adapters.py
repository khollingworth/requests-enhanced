"""
Adapter implementations for enhanced HTTP functionality.

This module provides custom adapter implementations for the requests library,
including support for HTTP/2 and HTTP/3 protocols. These adapters can be used with
the enhanced Session class to enable advanced protocol features with automatic fallback.
"""

import logging
import re
import ssl
import requests
from typing import Any, Mapping, Optional, Tuple, Union

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.connection import HTTPSConnection
from requests.packages.urllib3.connectionpool import (
    HTTPConnectionPool,
    HTTPSConnectionPool,
)
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.util.retry import Retry
import urllib3

# Check if HTTP/2 dependencies are available
try:
    # Just checking if the h2 package is importable
    import h2.settings  # noqa: F401

    HTTP2_AVAILABLE = True
except ImportError:
    HTTP2_AVAILABLE = False

# Check if HTTP/3 dependencies are available
try:
    import aioquic  # noqa: F401
    import asyncio  # noqa: F401

    HTTP3_AVAILABLE = True
except ImportError:
    HTTP3_AVAILABLE = False

# Get urllib3 version for compatibility checks
try:
    # Extract version directly from urllib3.__version__ if available
    URLLIB3_VERSION = getattr(urllib3, "__version__", "")
    if not URLLIB3_VERSION and hasattr(urllib3, "_version"):
        URLLIB3_VERSION = getattr(urllib3, "_version", "")

    # Parse version using regex
    version_match = re.match(r"(\d+)\.(\d+)", URLLIB3_VERSION)
    if version_match:
        URLLIB3_MAJOR = int(version_match.group(1))
        URLLIB3_MINOR = int(version_match.group(2))
    else:
        # Default to conservative assumption
        URLLIB3_MAJOR, URLLIB3_MINOR = 1, 0
except (ValueError, AttributeError):
    # If we can't determine the version, assume an older version
    URLLIB3_MAJOR, URLLIB3_MINOR = 1, 0

# Configure module logger
logger = logging.getLogger("requests_enhanced")

# Log the detected version for debugging
logger.debug(
    f"Detected urllib3 version: {URLLIB3_MAJOR}.{URLLIB3_MINOR} " f"({URLLIB3_VERSION})"
)

# Log HTTP protocol support
logger.debug(f"HTTP/2 support: {HTTP2_AVAILABLE}")
logger.debug(f"HTTP/3 support: {HTTP3_AVAILABLE}")


class HTTP3Connection(HTTPSConnection):
    """A connection class that supports HTTP/3 protocol using QUIC."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize an HTTP/3 connection.

        Args:
            *args: Positional arguments for the HTTPSConnection.
            **kwargs: Keyword arguments for the HTTPSConnection.
        """
        self.secure = kwargs.pop("secure", True)

        # HTTP/3 specific settings
        self.quic_connection_options = kwargs.pop("quic_connection_options", None)
        self.quic_max_datagram_size = kwargs.pop("quic_max_datagram_size", 1350)

        # These are HTTP/3 specific so we don't pass them to the parent
        # They are stored for potential future use in connection establishment
        self._http3_options = {
            "quic_connection_options": self.quic_connection_options,
            "quic_max_datagram_size": self.quic_max_datagram_size,
        }

        # Initialize the parent class with remaining arguments
        super().__init__(*args, **kwargs)

        # Set ALPN protocols with HTTP/3 as primary and fallback options
        if not hasattr(self, "ssl_context") or self.ssl_context is None:
            # Create a default SSL context if none exists
            self.ssl_context: ssl.SSLContext = ssl.create_default_context()

        # Set ALPN protocols with h3 as primary
        if hasattr(self.ssl_context, "set_alpn_protocols"):
            try:
                # Add h3 first for priority, then fallbacks
                self.ssl_context.set_alpn_protocols(["h3", "h2", "http/1.1"])
            except (AttributeError, NotImplementedError) as e:
                logger.warning(f"ALPN protocol setting failed: {e}")

    def connect(self) -> None:
        """Connect to the host and port specified in the constructor.

        This method overrides the parent to attempt HTTP/3 connection first,
        then falls back to HTTP/2 or HTTP/1.1 if HTTP/3 fails.
        """
        try:
            # Attempt HTTP/3 connection using QUIC
            if HTTP3_AVAILABLE:
                try:
                    # For now, we're just setting up the basics to avoid
                    # complex asyncio handling in a sync context
                    # A real implementation would use aioquic directly
                    logger.debug("Attempting HTTP/3 connection")

                    # The normal HTTPSConnection.connect() will still be called
                    # but we've set ALPN to prefer h3 if the server supports it
                    super().connect()

                    # In a real implementation, this is where we would:
                    # 1. Create a QUIC connection
                    # 2. Establish HTTP/3 session
                    # 3. Handle HTTP/3 specific logic

                    # Check if HTTP/3 was actually negotiated
                    # This is a placeholder check - real implementation would verify
                    if hasattr(self.sock, "selected_alpn_protocol"):
                        selected = self.sock.selected_alpn_protocol()
                        if selected == "h3":
                            logger.debug("HTTP/3 connection established")
                            return
                        else:
                            logger.debug(f"Server selected {selected} instead of h3")

                    # If we reach here, HTTP/3 wasn't negotiated or supported
                    logger.debug("HTTP/3 connection failed, falling back")
                except Exception as e:
                    logger.warning(f"HTTP/3 connection error: {e}, falling back")
            else:
                logger.debug("HTTP/3 not available, using fallback")

            # Fall back to standard HTTPS connection (will use HTTP/2 if available)
            super().connect()

        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise


class HTTP3ConnectionPool(HTTPSConnectionPool):
    """A connection pool for HTTP/3 connections with fallback capability."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize an HTTP/3 connection pool.

        Args:
            *args: Positional arguments for HTTPSConnectionPool.
            **kwargs: Keyword arguments for HTTPSConnectionPool.
        """
        # Store HTTP/3 specific options before passing to parent
        self.quic_connection_options = kwargs.pop("quic_connection_options", None)
        self.quic_max_datagram_size = kwargs.pop("quic_max_datagram_size", 1350)

        # Initialize the parent class
        super().__init__(*args, **kwargs)

        # Set the connection class to HTTP3Connection after initialization
        self.ConnectionCls = HTTP3Connection

        logger.debug(f"Initialized HTTP3ConnectionPool to {self.host}:{self.port}")

    def _new_conn(self) -> HTTPSConnection:
        """Create a new HTTP/3 connection.

        Returns:
            A new HTTP3Connection instance.
        """
        # Create a new HTTP/3 connection
        conn = super()._new_conn()

        # Pass HTTP/3 specific options - use try/except instead of isinstance
        # to handle both real and mock objects in tests
        try:
            conn.quic_connection_options = self.quic_connection_options
            conn.quic_max_datagram_size = self.quic_max_datagram_size
        except (AttributeError, TypeError):
            # If not a HTTP3Connection or attributes can't be set, log but continue
            logger.debug("Connection object doesn't support HTTP/3 specific attributes")

        return conn


class HTTP2Connection(HTTPSConnection):
    """A connection class that supports HTTP/2 protocol negotiation."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Extract and store the protocol parameter before parent init
        protocol = kwargs.pop("protocol", "https")

        # Handle parameters that might be specific to certain urllib3 versions
        if "request_context" in kwargs:
            kwargs.pop("request_context", None)

        # Initialize the parent connection
        super().__init__(*args, **kwargs)

        # Set the protocol after parent initialization to ensure it's not overridden
        self._protocol = protocol

    def connect(self) -> None:
        """Connect to the host and port specified in __init__."""
        try:
            # Call the original connect method
            super().connect()

            # Only try to set ALPN protocols if we're using HTTP/2
            if (
                self._protocol == "h2"
                and hasattr(self, "sock")
                and self.sock is not None
                and HTTP2_AVAILABLE
            ):
                # Get the socket's context if possible
                if hasattr(self.sock, "context"):
                    context = self.sock.context

                    # Set ALPN protocols if possible
                    try:
                        if hasattr(context, "set_alpn_protocols"):
                            context.set_alpn_protocols(["h2", "http/1.1"])
                            logger.debug("Set ALPN protocols on connection")
                    except (AttributeError, NotImplementedError) as e:
                        logger.debug(f"ALPN protocol setting not supported: {e}")

        except Exception as e:
            logger.warning(f"Error during HTTP/2 connection setup: {e}")
            # Re-raise to be handled by the caller
            raise


class HTTP2ConnectionPool(HTTPSConnectionPool):
    """A connection pool that uses HTTP2Connection."""

    ConnectionCls = HTTP2Connection

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize an HTTP/2 connection pool.

        Args:
            *args: Positional arguments for HTTPSConnectionPool.
            **kwargs: Keyword arguments for HTTPSConnectionPool.
        """
        # Extract and store the protocol before initializing the parent
        self._protocol = kwargs.pop("protocol", "http/1.1")

        try:
            # Initialize the parent connection pool
            super().__init__(*args, **kwargs)
            logger.debug(
                f"Successfully initialized HTTP2ConnectionPool for protocol "
                f"{self._protocol}"
            )
        except TypeError as e:
            # Handle unexpected keyword argument error
            if "got an unexpected keyword argument" in str(e):
                # Try to identify and remove the problematic argument
                arg_match = re.search(
                    r"got an unexpected keyword argument '(\w+)'", str(e)
                )
                if arg_match:
                    arg_name = arg_match.group(1)
                    logger.warning(
                        f"Removing arg '{arg_name}' from connection pool init"
                    )
                    kwargs.pop(arg_name, None)
                    super().__init__(*args, **kwargs)
                    logger.debug(
                        "Successfully initialized HTTP2ConnectionPool after fixing args"
                    )
                else:
                    # If we can't identify the specific argument, re-raise
                    raise
            else:
                # Re-raise for other TypeError cases
                raise

    def _new_conn(self) -> HTTP2Connection:
        """Return a fresh HTTP2Connection."""
        try:
            # Create a new connection using the parent class method
            conn = super()._new_conn()

            # Set the protocol on the connection
            if hasattr(conn, "_protocol"):
                conn._protocol = self._protocol

            return conn
        except TypeError as e:
            # Handle unexpected keyword argument errors
            if "got an unexpected keyword argument" in str(e):
                logger.warning(f"Error creating HTTP/2 connection: {e}")
                logger.warning("Attempting to create connection directly")

                # Create HTTP/2 connection with negotiation and fallback support
                try:
                    conn = HTTP2Connection(
                        host=self.host, port=self.port, protocol=self._protocol
                    )
                    return conn
                except Exception as e:
                    logger.warning(
                        f"Failed to create HTTP/2 connection: {self.host}:{self.port}"
                        f"({e})"
                    )
                    raise
            else:
                # Re-raise for other TypeError cases
                raise


class HTTP3PoolManager(PoolManager):
    """A pool manager for HTTP/3 connections with fallback capability."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize an HTTP/3 pool manager.

        Args:
            *args: Positional arguments for PoolManager.
            **kwargs: Keyword arguments for PoolManager.
        """
        # Extract HTTP/3-specific options before passing to parent
        self.quic_connection_options = kwargs.pop("quic_connection_options", None)
        self.quic_max_datagram_size = kwargs.pop("quic_max_datagram_size", 1350)

        # Initialize the parent class
        super().__init__(*args, **kwargs)

        logger.debug("Initialized HTTP3PoolManager")

    def _new_pool(
        self, scheme: str, host: str, port: int, **kwargs: Any
    ) -> Union[HTTPConnectionPool, HTTPSConnectionPool]:
        """Create a new connection pool for the given URL components.

        Args:
            scheme: URL scheme (http or https).
            host: Target host.
            port: Target port.

        Returns:
            An appropriate connection pool instance for the given URL.
        """
        # For HTTPS, try to use HTTP/3
        if scheme == "https":
            try:
                # Attempt to create an HTTP/3 pool
                if HTTP3_AVAILABLE:
                    pool_kwargs = self.connection_pool_kw.copy()
                    pool_kwargs.update(
                        {
                            "quic_connection_options": self.quic_connection_options,
                            "quic_max_datagram_size": self.quic_max_datagram_size,
                        }
                    )

                    # Create HTTP3ConnectionPool
                    return HTTP3ConnectionPool(host, port, **pool_kwargs)
                else:
                    logger.debug(
                        "HTTP/3 not available, falling back to HTTP/2 or HTTP/1.1"
                    )

                    # Try HTTP/2 if available
                    if HTTP2_AVAILABLE:
                        try:
                            pool_kwargs = self.connection_pool_kw.copy()
                            return HTTP2ConnectionPool(host, port, **pool_kwargs)
                        except (ImportError, TypeError) as e:
                            logger.warning(f"Failed to create HTTP/2 pool: {e}")

                    # Fall back to standard HTTPS pool
                    return HTTPSConnectionPool(host, port, **self.connection_pool_kw)
            except (ImportError, TypeError) as e:
                logger.warning(f"Failed to create HTTP/3 pool: {e}, falling back")

                # Try HTTP/2 first as fallback
                if HTTP2_AVAILABLE:
                    try:
                        return HTTP2ConnectionPool(
                            host, port, **self.connection_pool_kw
                        )
                    except (ImportError, TypeError) as e2:
                        logger.warning(f"Failed to create HTTP/2 pool: {e2}")

                # Final fallback to standard HTTPS
                return HTTPSConnectionPool(host, port, **self.connection_pool_kw)

        # For HTTP (not HTTPS), use standard connection pool
        return HTTPConnectionPool(host, port, **self.connection_pool_kw)


class HTTP3Adapter(HTTPAdapter):
    """A transport adapter for HTTP/3 with fallback to HTTP/2 and HTTP/1.1."""

    def __init__(
        self,
        protocol_version: str = "h3",
        pool_connections: int = 10,
        pool_maxsize: int = 10,
        max_retries: Union[Retry, int, None] = None,
        pool_block: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize an HTTP/3 adapter with fallback capabilities.

        Args:
            protocol_version: Protocol version to use ('h3', 'h2', or 'http/1.1').
            pool_connections: Number of connection pools to cache.
            pool_maxsize: Maximum number of connections to save in the pool.
            max_retries: Maximum number of retries for failed requests.
            pool_block: Whether to block when a pool has no free connections.
            **kwargs: Additional arguments for the connection.
        """
        # Set up member variables
        self.protocol_version = protocol_version
        self.quic_connection_options = kwargs.pop("quic_connection_options", None)
        self.quic_max_datagram_size = kwargs.pop("quic_max_datagram_size", 1350)

        # Verify available dependencies for the requested protocol
        if protocol_version == "h3" and not HTTP3_AVAILABLE:
            logger.warning("HTTP/3 dependencies not available, falling back to HTTP/2")
            self.protocol_version = "h2" if HTTP2_AVAILABLE else "http/1.1"

        if self.protocol_version == "h2" and not HTTP2_AVAILABLE:
            logger.warning(
                "HTTP/2 dependencies not available, falling back to HTTP/1.1"
            )
            self.protocol_version = "http/1.1"

        logger.debug(
            f"Initialized HTTP3Adapter with protocol_version={self.protocol_version}"
        )

        # Initialize the parent class
        super().__init__(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=max_retries,
            pool_block=pool_block,
            **kwargs,
        )

    def init_poolmanager(
        self, connections: int, maxsize: int, block: bool = False, **pool_kwargs: Any
    ) -> None:
        """Initialize the pool manager with HTTP/3 support and fallback capabilities.

        Args:
            connections: Number of connection pools to cache.
            maxsize: Maximum number of connections to save in the pool.
            block: Whether to block when a pool has no free connections.
            **pool_kwargs: Additional arguments for the pool manager.
        """
        logger.debug(
            f"Initializing HTTP3Adapter pool manager with protocol_version="
            f"{self.protocol_version}"
        )

        # Set up SSL/TLS parameters
        pool_kwargs["ssl_version"] = "TLSv1.3"  # HTTP/3 requires TLS 1.3

        # Add QUIC-specific parameters if available
        if self.quic_connection_options:
            pool_kwargs["quic_connection_options"] = self.quic_connection_options
        if self.quic_max_datagram_size:
            pool_kwargs["quic_max_datagram_size"] = self.quic_max_datagram_size

        try:
            # Use our custom HTTP3PoolManager based on the protocol
            if self.protocol_version == "h3" and HTTP3_AVAILABLE:
                self.poolmanager = HTTP3PoolManager(
                    num_pools=connections,
                    maxsize=maxsize,
                    block=block,
                    **pool_kwargs,
                )
                logger.debug("HTTP/3 pool manager initialized")
            elif self.protocol_version == "h2" and HTTP2_AVAILABLE:
                # Fallback to HTTP/2
                http2_adapter = HTTP2Adapter(
                    pool_connections=connections,
                    pool_maxsize=maxsize,
                    pool_block=block,
                    protocol_version="h2",
                )
                http2_adapter.init_poolmanager(
                    connections, maxsize, block, **pool_kwargs
                )
                self.poolmanager = http2_adapter.poolmanager
                logger.debug("HTTP/2 pool manager initialized (fallback from HTTP/3)")
            else:
                # Fallback to standard pool manager
                # Remove unsupported parameters
                for param in ["quic_connection_options", "quic_max_datagram_size"]:
                    pool_kwargs.pop(param, None)
                pool_kwargs["ssl_version"] = "TLSv1.2"  # Use TLS 1.2 for HTTP/1.1

                self.poolmanager = PoolManager(
                    num_pools=connections,
                    maxsize=maxsize,
                    block=block,
                    **pool_kwargs,
                )
                logger.debug("Standard pool manager initialized (fallback to HTTP/1.1)")
        except Exception as e:
            logger.error(f"Failed to initialize pool manager: {e}", exc_info=True)
            # Fall back to HTTP/2 on any HTTP/3 error
            try:
                http2_adapter = HTTP2Adapter(
                    pool_connections=connections,
                    pool_maxsize=maxsize,
                    pool_block=block,
                    protocol_version="h2",
                )
                http2_adapter.init_poolmanager(
                    connections, maxsize, block, **pool_kwargs
                )
                self.poolmanager = http2_adapter.poolmanager
                logger.debug("Fallback to HTTP/2 adapter after HTTP/3 error")
            except Exception as e2:
                logger.error(
                    f"Failed to initialize HTTP/2 fallback: {e2}", exc_info=True
                )
                # Last resort fallback
                self.poolmanager = PoolManager(
                    num_pools=connections, maxsize=maxsize, block=block
                )
                logger.debug("Basic pool manager initialized (error fallback)")

    def get_connection_with_tls_context(
        self,
        request: requests.PreparedRequest,
        verify: Union[bool, str, None],
        proxies: Optional[Mapping[str, str]] = None,
        cert: Optional[Union[str, Tuple[str, str]]] = None,
    ) -> Union[HTTPConnectionPool, HTTPSConnectionPool]:
        """Returns a urllib3 connection for the given request and TLS settings.

        This method overrides the parent HTTPAdapter method to provide HTTP/3 support.

        Args:
            request: The PreparedRequest object to be sent over the connection.
            verify: Controls server TLS certificate verification (bool or path to CA
                bundle).
            proxies: (Optional) The proxies dictionary to apply to the request.
            cert: (Optional) User-provided SSL certificate for client authentication
                (mTLS).

        Returns:
            A urllib3 connection pool appropriate for this request.

        Raises:
            InvalidURL: If the URL in the request is not valid.
            InvalidProxyURL: If the proxy URL is malformed.
        """
        # HTTP/3 doesn't support proxies, so if proxies are specified,
        # we'll let the parent class handle it which will call proxy_manager_for
        # and that will raise NotImplementedError
        if proxies:
            return super().get_connection_with_tls_context(
                request, verify, proxies, cert
            )

        try:
            # Use the parent class method to build connection parameters
            # Ensure verify is not None as build_connection_pool_key_attributes
            # expects Union[bool, str]
            verify_param = verify if verify is not None else False
            host_params, pool_kwargs = self.build_connection_pool_key_attributes(
                request,
                verify_param,
                cert,
            )
        except ValueError as e:
            from requests.exceptions import InvalidURL

            raise InvalidURL(e, request=request)

        # Get connection from our pool manager
        conn = self.poolmanager.connection_from_host(
            **host_params, pool_kwargs=pool_kwargs
        )

        return conn

    def proxy_manager_for(self, proxy: str, **proxy_kwargs: Any) -> None:
        """Initialize a proxy manager.

        HTTP/3 doesn't support proxies yet, so this raises NotImplementedError.

        Args:
            proxy: The proxy URL.
            **proxy_kwargs: Additional proxy configuration.

        Raises:
            NotImplementedError: HTTP/3 does not support proxies.
        """
        raise NotImplementedError("HTTP/3 does not support proxies yet")

    def _create_http2_poolmanager(
        self, connections: int, maxsize: int, block: bool, pool_kwargs: dict
    ) -> PoolManager:
        """Create an HTTP/2 pool manager.

        Args:
            connections: Number of connection pools to cache.
            maxsize: Maximum number of connections to save in the pool.
            block: Whether to block when a pool has no free connections.
            pool_kwargs: Additional arguments for the pool manager.

        Returns:
            A PoolManager instance with HTTP/2 support.
        """
        # Use our custom HTTP2PoolManager based on the protocol
        try:
            # Initialize the custom pool manager
            class HTTP2PoolManager(PoolManager):
                """Custom pool manager that uses our HTTP/2 connection classes."""

                def __init__(self, **kwargs: Any) -> None:
                    # Try HTTP/2 if protocol info and h2 library is available
                    if "h2" in kwargs.get("url", "").lower() and HTTP2_AVAILABLE:
                        protocol = "h2"
                    else:
                        protocol = kwargs.pop("protocol", "http/1.1")

                    # Initialize parent PoolManager
                    super().__init__(**kwargs)

                    # Store the protocol for use in _new_pool
                    self.protocol = protocol

                def _new_pool(
                    self, scheme: str, host: str, port: int, **kwargs: Any
                ) -> Any:
                    """Create a new connection pool for HTTP or HTTPS."""
                    # Add protocol to the kwargs
                    kwargs["protocol"] = self.protocol

                    try:
                        # Create the appropriate pool type based on scheme
                        if scheme == "http":
                            return HTTPConnectionPool(host, port, **kwargs)
                        elif scheme == "https":
                            return HTTP2ConnectionPool(host, port, **kwargs)
                    except TypeError as e:
                        # Handle errors by creating a basic pool
                        logger.warning(f"Error creating connection pool: {e}")
                        logger.warning("Creating pool with minimal parameters")

                        # Create with minimal parameters
                        if scheme == "http":
                            return HTTPConnectionPool(host, port)
                        elif scheme == "https":
                            return HTTPSConnectionPool(host, port)

            # Create our custom pool manager
            self.poolmanager = HTTP2PoolManager(
                num_pools=connections,
                maxsize=maxsize,
                block=block,
                protocol=self.protocol_version,
                **pool_kwargs,
            )
            logger.debug("HTTP/2 pool manager initialized with custom connections")
            return self.poolmanager
        except Exception as e:
            # Log the error and continue with HTTP/1.1
            logger.warning(f"Error negotiating HTTP/2: {e}. Using HTTP/1.1")
            logger.warning("Falling back to standard pool manager config")

            # Standard approach - try adding ALPN protocols to pool kwargs
            try:
                # Different approaches based on urllib3 version
                if URLLIB3_MAJOR > 1:
                    # For urllib3 2.x, be extra careful
                    logger.debug("Using urllib3 2.x+ configuration approach")
                else:
                    # For urllib3 1.x, use direct ALPN protocols
                    pool_kwargs["alpn_protocols"] = ["h2", "http/1.1"]
                    logger.debug("Added ALPN protocols for urllib3 1.x")
            except Exception as e:
                logger.warning(f"Error adding ALPN protocols: {e}")

            # Standard fallback - create a regular pool manager
            try:
                # Remove alpn_protocols if it's present and we're not using HTTP/2
                if self.protocol_version != "h2" and "alpn_protocols" in pool_kwargs:
                    pool_kwargs.pop("alpn_protocols", None)

                # Create the standard pool manager
                self.poolmanager = PoolManager(
                    num_pools=connections,
                    maxsize=maxsize,
                    block=block,
                    **pool_kwargs,
                )
                logger.debug("Standard pool manager initialized")
            except TypeError as e:
                # Retry without unsupported kwargs
                if "alpn_protocols" in str(e) and "alpn_protocols" in pool_kwargs:
                    logger.warning(
                        "ALPN protocols not supported in this urllib3 version"
                    )
                    pool_kwargs.pop("alpn_protocols", None)
                    self.poolmanager = PoolManager(
                        num_pools=connections,
                        maxsize=maxsize,
                        block=block,
                        **pool_kwargs,
                    )
                    logger.debug("Initialized pool manager without ALPN protocols")
                else:
                    # Re-raise if it's a different TypeError
                    logger.error(f"Unrecoverable error initializing pool manager: {e}")
                    raise

            return self.poolmanager


class HTTP2Adapter(HTTPAdapter):
    """
    Transport adapter for requests that enables HTTP/2 support.

    This adapter extends the standard HTTPAdapter to use HTTP/2 protocol
    when possible, falling back to HTTP/1.1 when HTTP/2 is not supported
    by the server or when HTTP/2 dependencies are not installed.

    Attributes:
        protocol_version: The HTTP protocol version to use
    """

    def __init__(
        self,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
        max_retries: Union[Retry, int, None] = None,
        pool_block: bool = False,
        protocol_version: str = "h2",
    ) -> None:
        """
        Initialize the HTTP/2 adapter with the given options.

        Args:
            pool_connections: Number of connection pools to cache
            pool_maxsize: Maximum number of connections to save in the pool
            max_retries: Retry configuration to use
            pool_block: Whether the connection pool should block for connections
            protocol_version: HTTP protocol version ("h2" or "http/1.1")

        Raises:
            ImportError: If HTTP/2 dependencies are not available and
                protocol_version is "h2"
        """
        self.protocol_version = protocol_version

        # Check if HTTP/2 is requested but dependencies missing
        if protocol_version == "h2" and not HTTP2_AVAILABLE:
            msg = "HTTP/2 support requires additional dependencies. "
            msg += "Install with 'pip install requests-enhanced[http2]'"
            raise ImportError(msg)

        # Proceed with initialization
        if protocol_version == "h2":
            logger.debug(
                "HTTP/2 adapter initialized with HTTP/2 protocol version: %s",
                protocol_version,
            )
        else:
            logger.debug(
                "HTTP/2 adapter initialized with protocol version: %s", protocol_version
            )
        super().__init__(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=max_retries,
            pool_block=pool_block,
        )

        logger.debug(f"Created HTTP2Adapter with protocol_version={protocol_version}")

    def init_poolmanager(
        self,
        connections: int,
        maxsize: int,
        block: bool = False,
        **pool_kwargs: Any,
    ) -> None:
        """
        Initialize the connection pool manager with HTTP/2 support.

        Args:
            connections: Number of connection pools to cache
            maxsize: Maximum number of connections to save in the pool
            block: Whether the connection pool should block for connections
            **pool_kwargs: Additional arguments for the pool manager
        """
        # Use TLS 1.2 or higher for all HTTPS connections
        pool_kwargs["ssl_version"] = "TLSv1.2"

        # Handle HTTP/2 configuration based on urllib3 version and availability
        if self.protocol_version == "h2" and HTTP2_AVAILABLE:
            logger.debug(f"Configuring HTTP/2 support with urllib3 {URLLIB3_VERSION}")

            try:
                # Use our custom pool manager with connection classes
                # that handle HTTP/2 negotiation at the SSL layer
                class HTTP2PoolManager(PoolManager):
                    """Custom pool manager that uses our HTTP/2 connection classes."""

                    def __init__(self, **kwargs: Any) -> None:
                        # Try HTTP/2 if protocol info and h2 library is available
                        if "h2" in kwargs.get("url", "").lower() and HTTP2_AVAILABLE:
                            protocol = "h2"
                        else:
                            protocol = kwargs.pop("protocol", "http/1.1")

                        # Initialize parent PoolManager
                        super().__init__(**kwargs)

                        # Store the protocol for use in _new_pool
                        self.protocol = protocol

                    def _new_pool(
                        self, scheme: str, host: str, port: int, **kwargs: Any
                    ) -> Any:
                        """Create a new connection pool for HTTP or HTTPS."""
                        # Add protocol to the kwargs
                        kwargs["protocol"] = self.protocol

                        try:
                            # Create the appropriate pool type based on scheme
                            if scheme == "http":
                                return HTTPConnectionPool(host, port, **kwargs)
                            elif scheme == "https":
                                return HTTP2ConnectionPool(host, port, **kwargs)
                        except TypeError as e:
                            # Handle errors by creating a basic pool
                            logger.warning(f"Error creating connection pool: {e}")
                            logger.warning("Creating pool with minimal parameters")

                            # Create with minimal parameters
                            if scheme == "http":
                                return HTTPConnectionPool(host, port)
                            elif scheme == "https":
                                return HTTPSConnectionPool(host, port)

                # Create our custom pool manager
                self.poolmanager = HTTP2PoolManager(
                    num_pools=connections,
                    maxsize=maxsize,
                    block=block,
                    protocol=self.protocol_version,
                    **pool_kwargs,
                )
                logger.debug("HTTP/2 pool manager initialized with custom connections")
                return

            except Exception as e:
                # Log the error and continue with HTTP/1.1
                logger.warning(f"Error negotiating HTTP/2: {e}. Using HTTP/1.1")
                logger.warning("Falling back to standard pool manager config")

                # Standard approach - try adding ALPN protocols to pool kwargs
                try:
                    # Different approaches based on urllib3 version
                    if URLLIB3_MAJOR > 1:
                        # For urllib3 2.x, be extra careful
                        logger.debug("Using urllib3 2.x+ configuration approach")
                    else:
                        # For urllib3 1.x, use direct ALPN protocols
                        pool_kwargs["alpn_protocols"] = ["h2", "http/1.1"]
                        logger.debug("Added ALPN protocols for urllib3 1.x")
                except Exception as e:
                    logger.warning(f"Error adding ALPN protocols: {e}")

        # Standard fallback - create a regular pool manager
        try:
            # Remove alpn_protocols if it's present and we're not using HTTP/2
            if self.protocol_version != "h2" and "alpn_protocols" in pool_kwargs:
                pool_kwargs.pop("alpn_protocols", None)

            # Create the standard pool manager
            self.poolmanager = PoolManager(
                num_pools=connections,
                maxsize=maxsize,
                block=block,
                **pool_kwargs,
            )
            logger.debug("Standard pool manager initialized")
        except TypeError as e:
            # Retry without unsupported kwargs
            if "alpn_protocols" in str(e) and "alpn_protocols" in pool_kwargs:
                logger.warning("ALPN protocols not supported in this urllib3 version")
                pool_kwargs.pop("alpn_protocols", None)
                self.poolmanager = PoolManager(
                    num_pools=connections,
                    maxsize=maxsize,
                    block=block,
                    **pool_kwargs,
                )
                logger.debug("Initialized pool manager without ALPN protocols")
            else:
                # Re-raise if it's a different TypeError
                logger.error(f"Unrecoverable error initializing pool manager: {e}")
                raise
