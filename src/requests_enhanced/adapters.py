"""
Adapter implementations for enhanced HTTP functionality.

This module provides custom adapter implementations for the requests library,
including support for HTTP/2 protocol. These adapters can be used with
the enhanced Session class to enable advanced protocol features.
"""

import logging
import re
from typing import Any, Union

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


class HTTP2Connection(HTTPSConnection):
    """A connection class that supports HTTP/2 protocol negotiation."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Remove parameters that might not be supported in this version
        self._protocol = kwargs.pop("protocol", "http/1.1")

        # Handle parameters that might be specific to certain urllib3 versions
        if "request_context" in kwargs:
            kwargs.pop("request_context", None)

        # Initialize the parent connection
        super().__init__(*args, **kwargs)

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
                # Socket level protocol negotiation requires ssl
                context = self.sock.context

                # Get the socket's context if possible
                if hasattr(self.sock, "context"):
                    context = self.sock.context

                    # Set ALPN protocols if possible
                    try:
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
