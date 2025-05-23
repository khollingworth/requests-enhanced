# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-05-23

### Added
- **Major Version Release** with complete OAuth integration
- Comprehensive documentation updates in README.md and docs/
- Improved example coverage with extensive OAuth examples
- Full HTTP/1.1, HTTP/2, and HTTP/3 protocol support with OAuth

### Changed
- Upgraded all documentation to reflect v1.0.0 status
- Refined error handling with more descriptive messages
- Enhanced CI/CD pipeline for v1.0.0 release

### Fixed
- All test failures related to OAuth integration
- HTTP/3 adapter connection issues in test suite
- Documentation inconsistencies and outdated references

## [0.2.0] - 2025-05-23

### Added
- **OAuth 1.0/1.1 Support**: Complete OAuth 1.0/1.1 authentication implementation
  - `OAuth1EnhancedSession` class for OAuth 1.0/1.1 flows
  - Support for request token, authorization, and access token flows
  - Compatible with Twitter API, Flickr, and other OAuth 1.0 services
- **OAuth 2.0 Support**: Comprehensive OAuth 2.0 authentication implementation
  - `OAuth2EnhancedSession` class for OAuth 2.0 flows
  - Authorization code flow, client credentials flow support
  - Automatic token refresh with configurable callbacks
  - Compatible with GitHub, Google, Facebook, and other OAuth 2.0 providers
- **OAuth Dependencies**: New `[oauth]` extra for optional OAuth functionality
  - `requests-oauthlib` and `oauthlib` dependencies
  - Graceful fallback when OAuth dependencies not installed
- **OAuth Documentation**: Comprehensive OAuth usage guide and examples
  - Complete usage guide at `docs/oauth-usage-guide.md`
  - Real-world examples in `examples/oauth_example.py`
  - Integration with enhanced session features (HTTP/2, HTTP/3, retries)
- **OAuth Error Handling**: Custom `OAuthNotAvailableError` exception
- **OAuth Testing**: Comprehensive test suite with 95% coverage for OAuth module

### Changed
- **Package Description**: Updated to include OAuth authentication capabilities
- **Installation Options**: Added `pip install requests-enhanced[oauth]` option
- **README**: Enhanced with OAuth features and documentation links
- **API Exports**: Added OAuth classes to public API when available

### Technical Details
- OAuth sessions inherit all enhanced session capabilities (HTTP/2, HTTP/3, retries, timeouts)
- Optional dependency loading with proper error handling
- Thread-safe token management and automatic refresh
- Secure token storage patterns and best practices documentation
- Full compatibility with existing `requests-oauthlib` workflows

## [0.1.18] - 2025-05-23

### Fixed
- Updated PyPI badge to use shields.io for better reliability and caching
- Fixed badge display issues in README

## [0.1.17] - 2025-05-23

### Changed
- Updated PyPI package description to include HTTP/2 and HTTP/3 support
- Enhanced README.md features section to highlight HTTP/3 capabilities
- Added HTTP/3 installation instructions in documentation

## [0.1.16] - 2025-05-23

### Fixed
- Fixed HTTP2Connection protocol parameter preservation by setting it after parent class initialization
- Resolved issue where parent HTTPSConnection class was overriding the protocol attribute
- Both test_http2_connection_init and test_http2_connection_connect_http2 now pass correctly
- Ensured HTTP/2 protocol negotiation works as expected

## [0.1.15] - 2025-05-23

### Fixed
- Fixed HTTP2Connection protocol parameter handling to properly store the "h2" protocol when specified
- Improved ALPN protocol setting logic in HTTP2Connection.connect() method to properly check for context availability
- Resolved CI test failures in test_http2_connection_init and test_http2_connection_connect_http2

## [0.1.14] - 2025-05-23

### Added
- Added security vulnerability scanning to CI pipeline using the safety tool
- Added comprehensive version constraints for all dependencies to prevent conflicts

### Changed
- Updated urllib3 dependency to constrain to versions <2.0.0 for better compatibility with boto/botocore
- Improved dependency management with proper upper bounds for all requirements

### Security
- Added explicit version constraints to prevent dependency conflicts with common packages
- Integrated automated security scanning to detect vulnerabilities before publishing

## [0.1.13] - 2025-05-23

### Added
- Implemented `get_connection_with_tls_context` method in HTTP3Adapter to replace deprecated `get_connection`
- Added comprehensive type annotations to HTTP/3 implementation for better IDE support
- Created consolidated `usage_guide.md` document for improved documentation structure

### Changed
- Updated API reference documentation to fully describe HTTP/3 support and fallback mechanisms
- Restructured documentation to be more comprehensive and better organized
- Added HTTP/3 protocol examples with automatic fallback demonstration

### Fixed
- Fixed all mypy type checking issues in HTTP/3 adapter implementation
- Fixed linting issues and long lines in HTTP/3 adapter
- Improved error handling in the HTTP/3 fallback mechanism

## [0.1.12] - 2025-05-23

### Added
- Added PLANNING.md file documenting project architecture and conventions
- Added PyPI Trusted Publisher setup documentation
- Added attestations generation for package releases

### Changed
- Migrated CI/CD pipeline from token-based authentication to PyPI Trusted Publisher (OIDC)
- Enhanced security with cryptographic attestations for published packages
- Updated GitHub Actions workflow with required OIDC permissions

### Fixed
- Fixed all HTTP/3 test failures by handling fallback scenarios properly
- Fixed test assertions to check HTTP3_AVAILABLE before expecting HTTP/3 behavior
- Added appropriate test skips for HTTP/3-specific functionality

## [0.1.11] - 2025-05-22

### Added
- Added HTTP/3 protocol support with automatic fallback capability
- Added HTTP3Adapter for handling HTTP/3 connections with QUIC transport
- Added HTTP3Connection and HTTP3ConnectionPool classes
- Added detection for HTTP/3 dependencies via HTTP3_AVAILABLE flag
- Added comprehensive test suite for HTTP/3 functionality with 80%+ coverage
- Added HTTP/3 usage example with performance comparison
- Added automatic protocol negotiation with fallback from HTTP/3 → HTTP/2 → HTTP/1.1
- Added new `[http3]` and `[all]` extras for dependency installation

### Changed
- Enhanced Session class to support HTTP/3 via `http_version="3"` parameter
- Improved adapter mounting with cleaner protocol fallback mechanism
- Updated adapter initialization to handle errors more gracefully
- Enhanced logging for protocol negotiation and fallback

## [0.1.10] - 2025-05-22

### Added
- Added manual workflow trigger support for CI pipeline
- Added HTTP/2 dependencies to CI test environment
- Added comprehensive test suite for HTTP/2 connections and adapters
- Created new test files to specifically target HTTP/2 functionality

### Fixed
- Improved test skipping for environments without HTTP/2 dependencies
- Enhanced CI robustness with better error handling
- Fixed documentation link checking in CI workflow

### Improved
- Significantly increased test coverage from 63% to 87%
- Boosted HTTP/2 adapter coverage from 40% to 82%
- Enhanced test robustness by testing edge cases and error handling

## [0.1.9] - 2025-05-22

### Added
- Enhanced HTTP/2 documentation with detailed performance benefits
- Added comprehensive compatibility information for HTTP/2 support
- Included HTTP/2 performance benchmarks showing 30-40% speed improvements
- Expanded API reference with HTTP/2 configuration options

### Fixed
- Fixed code quality issues across the codebase (linting and formatting)
- Improved logging for HTTP/2 connection errors
- Enhanced tests for HTTP/2 adapter to ensure reliability

## [0.1.8] - 2025-05-22

### Fixed
- Fixed HTTP/2 adapter compatibility with different urllib3 versions
- Improved error handling in HTTP/2 connection classes
- Added graceful fallback mechanisms for HTTP/2 protocol negotiation
- Enhanced HTTP/2 adapter to work across Python environments

## [0.1.7] - 2025-05-22

### Added
- Added HTTP/2 protocol support for improved performance
- Added HTTP2Adapter class for handling HTTP/2 connections
- Added HTTP2_AVAILABLE flag to check for HTTP/2 dependency availability
- Added optional HTTP/2 dependencies available via `pip install requests-enhanced[http2]`
- Added comprehensive documentation and examples for HTTP/2 usage

## [0.1.6] - 2025-05-22

### Added
- Added test coverage for 100% code coverage
- Added tests for exception handling edge cases
- Added tests for session validation logic

### Changed
- Improved code formatting with flake8 and black
- Removed unused imports to reduce overhead
- Fixed line length issues for better readability

## [0.1.5] - 2025-05-21

### Changed
- Updated all documentation to consistently use 'requests-enhanced' package name
- Improved security by removing sensitive files from repository tracking
- Enhanced .gitignore to prevent committing credentials and environment-specific files

## [0.1.4] - 2025-05-21

### Fixed
- Resolved timeout handling issues in retry mechanism
- Fixed race condition in session initialization
- Improved error messages for better troubleshooting

## [0.1.3] - 2025-05-18

### Added
- Support for custom header management
- Added automatic payload compression
- New option for certificate verification toggle

### Fixed
- Corrected logging inconsistencies across session instances

## [0.1.2] - 2025-05-10

### Added
- Session pooling capabilities for enhanced performance
- HTTP/2 protocol support
- Debug mode with detailed connection information

### Changed
- Optimized retry algorithm for better performance
- Updated documentation with advanced usage examples

## [0.1.1] - 2025-05-05

### Added
- Connection pooling enhancements
- Session persistence options
- Additional utility functions for file uploads

### Fixed
- Addressed thread safety issues in concurrent requests
- Fixed memory leak in long-running sessions

## [0.1.0] - 2025-04-28

### Added
- Initial release of the requests-enhanced library (renamed from requests-plus)
- Enhanced Session class with automatic retry functionality
- Configurable timeout settings for all requests
- Custom exception classes for improved error handling
- Standardized logging with configurable formats
- Utility functions for common request patterns (json_get, json_post)
- Comprehensive test suite with 94% code coverage
- Complete documentation with API reference
- Published to PyPI at https://pypi.org/project/requests-enhanced/