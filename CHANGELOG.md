# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - Phase 1 Refactoring Complete ✅ - 2025-06-08

### Added - Phase 1 Complete Refactoring (18/18 Modules)

**Major Achievement**: Successfully refactored monolithic `topyaz.py` (1750+ lines) into a clean, modular architecture with 18+ focused modules.

#### ✅ **Phase 1a: Core Infrastructure** (4/4 COMPLETED)

- `core/errors.py`: Custom exception hierarchy with 6 error types (TopazError, AuthenticationError, EnvironmentError, ProcessingError, RemoteExecutionError, ValidationError)
- `core/types.py`: Comprehensive type definitions with dataclasses, enums (Product, LogLevel), and type aliases using Python 3.10+ union syntax
- `core/config.py`: YAML configuration management with environment variable support and dot notation access
- `utils/logging.py`: Professional logging with loguru integration, file rotation, and multiple handlers

#### ✅ **Phase 1b: System Components** (4/4 COMPLETED)

- `system/environment.py`: Environment validation for macOS versions, memory (16GB+), and disk space (80GB+)
- `system/gpu.py`: Multi-platform GPU detection (NVIDIA, AMD, Intel, Apple Metal) with utilization monitoring
- `system/memory.py`: Intelligent memory management with batch size optimization for different operations
- `system/paths.py`: Robust path validation with permission checks and cross-platform compatibility

#### ✅ **Phase 1c: Execution Layer** (4/4 COMPLETED)

- `execution/base.py`: Abstract interfaces with CommandExecutor and ProgressAwareExecutor base classes
- `execution/local.py`: Local command execution with real-time progress monitoring and subprocess management
- `execution/remote.py`: SSH remote execution with paramiko, connection pooling, and SFTP file transfer
- `execution/progress.py`: Rich progress monitoring with console, logging, and silent callback modes

#### ✅ **Phase 1d: Product Implementations** (4/4 COMPLETED)

- `products/base.py`: Abstract product interfaces with TopazProduct and MacOSTopazProduct base classes
- `products/_gigapixel.py`: Gigapixel AI implementation with Pro license validation and all CLI parameters
- `products/_video_ai.py`: Video AI implementation with FFmpeg integration and environment variable setup
- `products/_photo_ai.py`: Photo AI implementation with intelligent 450-image batch limit handling

#### ✅ **Phase 1e: Integration** (2/2 COMPLETED)

- `cli.py`: Simplified TopyazCLI class with dependency injection and component delegation
- Entry points: Updated `__main__.py` and `__init__.py` with backward compatibility and proper exports

#### ✅ **Phase 1f: Testing & Validation** (2/2 COMPLETED)

- `tests/test_refactoring.py`: Comprehensive test suite validating all new modules
- Backward compatibility: Full CLI interface compatibility maintained with original topyaz.py behavior

### Architectural Benefits Achieved

- **Modularity**: 18+ focused modules following Single Responsibility Principle
- **Type Safety**: Comprehensive type hints throughout with mypy compatibility
- **Testability**: Injectable dependencies and abstract interfaces enable unit testing
- **Maintainability**: Clear module structure with excellent code discoverability
- **Extensibility**: Abstract base classes enable easy addition of new products
- **Performance**: Memory-aware batch processing and GPU utilization optimization
- **Configuration**: Flexible YAML configuration with environment variable override
- **Error Handling**: Structured exception hierarchy with informative error messages
- **Remote Execution**: Production-ready SSH execution with connection management
- **Progress Monitoring**: Beautiful console progress bars and configurable logging

## [0.1.0-dev3] - 2024-12-10

### Fixed

- **Critical Issue #1**: Fixed Gigapixel AI executable not found error

  - Updated `_find_executable` function with correct macOS application paths
  - Gigapixel AI now correctly found at `/Applications/Topaz Gigapixel AI.app/Contents/Resources/bin/_gigapixel`
  - Photo AI now correctly found at `/Applications/Topaz Photo AI.app/Contents/Resources/bin/tpai`
  - Video AI now correctly found at `/Applications/Topaz Video AI.app/Contents/MacOS/ffmpeg`

- **Critical Issue #2**: Fixed Photo AI "Invalid argument" error (return code 253)

  - Corrected boolean parameter formatting for Photo AI CLI
  - When enabling features: pass just the flag (e.g., `--upscale`)
  - When disabling features: pass flag with `enabled=false` (e.g., `--upscale enabled=false`)

- **Critical Issue #3**: Improved Video AI authentication validation
  - Enhanced `_validate_video_ai_auth` function to check multiple auth file locations
  - Added correct auth file path: `/Applications/Topaz Video AI.app/Contents/Resources/models/auth.tpz`
  - Improved logging levels (debug vs warning vs info) for better user experience
  - Authentication validation now continues processing even if auth files not found (normal for GUI login)
  - Only warns if auth files exist but are invalid

### Changed

- Updated executable path detection logic for all three Topaz products on macOS
- Improved error handling and user feedback throughout the codebase
- Enhanced authentication validation to be more robust and user-friendly

### Technical

- Cleaned up import statements and code formatting using ruff and autoflake
- Fixed various linter warnings and code style issues
- Maintained backward compatibility while improving functionality

All three critical issues identified in the TODO list have been resolved. The CLI should now work correctly with properly installed Topaz applications on macOS.

## [0.1.0-dev2] - 2024-12-09

### Added

- Initial implementation of unified CLI wrapper for Topaz Labs products
- Support for Gigapixel AI, Photo AI, and Video AI processing
- SSH remote execution capabilities
- Progress monitoring and error recovery mechanisms
- Comprehensive logging with loguru
- CLI interface using Python Fire

### Documentation

- Extensive specification document (SPEC.md)
- Detailed README with installation and usage instructions
- TODO roadmap for future development

### Architecture

- Unified `TopyazCLI` class design
- Modular approach for different Topaz products
- Environment validation and setup
- GPU monitoring and resource management
