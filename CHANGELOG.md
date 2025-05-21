# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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