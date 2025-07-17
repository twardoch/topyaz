# Build System Documentation

This document describes the comprehensive build, test, and release system for the topyaz project.

## Overview

The topyaz project uses a modern Python packaging system with git-tag-based semantic versioning, comprehensive testing, and automated CI/CD with multiplatform binary releases.

## Key Features

- **Git-tag-based semversioning**: Automatic version management from git tags
- **Comprehensive test suite**: Unit, integration, and benchmark tests
- **Multiplatform CI/CD**: GitHub Actions for Linux, macOS, and Windows
- **Binary releases**: Standalone executables for each platform
- **Convenient scripts**: Easy-to-use build and test scripts
- **Makefile support**: Traditional make targets for common tasks

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Git
- Make (optional, for Makefile targets)

### Installation

```bash
# Install in development mode
make install
# or
python scripts/dev.py install
```

### Running Tests

```bash
# Run tests with coverage
make test-coverage
# or
python scripts/test.py --coverage --parallel

# Run all tests including benchmarks
make test-all
# or
python scripts/test.py --coverage --parallel --benchmark
```

### Building

```bash
# Build Python package
make build
# or
python scripts/build.py --clean --check

# Build binary executable
python scripts/build_binary.py --clean --install-deps
```

### Full Development Workflow

```bash
# Run complete development pipeline
make dev
# or
python scripts/dev.py ci
```

## Scripts

### Core Scripts

All scripts are located in the `scripts/` directory:

- **`dev.py`**: Main development interface with subcommands
- **`build.py`**: Build Python packages (wheel and sdist)
- **`test.py`**: Run tests with various options
- **`release.py`**: Release management and publishing
- **`build_binary.py`**: Build standalone binary executables

### Development Script (`scripts/dev.py`)

The main development interface with the following commands:

```bash
# Install package in development mode
python scripts/dev.py install

# Run tests
python scripts/dev.py test [--coverage] [--parallel] [--benchmark]

# Build package
python scripts/dev.py build [--clean] [--check]

# Run linting
python scripts/dev.py lint [--fix]

# Clean build artifacts
python scripts/dev.py clean

# Run full CI pipeline
python scripts/dev.py ci

# Release package
python scripts/dev.py release VERSION [--dry-run] [--repository testpypi]
```

### Build Script (`scripts/build.py`)

Builds Python packages with comprehensive validation:

```bash
# Build both wheel and source distribution
python scripts/build.py

# Build only wheel
python scripts/build.py --type wheel

# Clean before building and check metadata
python scripts/build.py --clean --check
```

### Test Script (`scripts/test.py`)

Comprehensive testing with multiple options:

```bash
# Basic test run
python scripts/test.py

# Tests with coverage and parallel execution
python scripts/test.py --coverage --parallel

# Run with linting
python scripts/test.py --lint

# Run only benchmark tests
python scripts/test.py --benchmark

# Run specific test markers
python scripts/test.py --markers "unit"
python scripts/test.py --markers "integration"
```

### Release Script (`scripts/release.py`)

Handles the complete release process:

```bash
# Release to PyPI
python scripts/release.py 1.0.0

# Dry run release
python scripts/release.py 1.0.0 --dry-run

# Release to test PyPI
python scripts/release.py 1.0.0 --repository testpypi

# Skip certain steps
python scripts/release.py 1.0.0 --skip-checks --skip-github
```

### Binary Build Script (`scripts/build_binary.py`)

Creates standalone executables:

```bash
# Build binary for current platform
python scripts/build_binary.py

# Build with dependencies installation
python scripts/build_binary.py --install-deps

# Clean build and skip testing
python scripts/build_binary.py --clean --no-test
```

## Makefile Targets

The project includes a Makefile with convenient targets:

```bash
# Show all available targets
make help

# Development workflow
make install          # Install in development mode
make test            # Run tests
make test-coverage   # Run tests with coverage
make lint            # Run linting
make build           # Build package
make clean           # Clean build artifacts
make dev             # Full development workflow

# Release workflow
make release VERSION=1.0.0      # Release to PyPI
make release-test VERSION=1.0.0 # Release to test PyPI
make release-dry VERSION=1.0.0  # Dry run release

# Git helpers
make tag VERSION=1.0.0  # Create git tag
make git-status         # Show git status
make git-log           # Show recent commits
make info              # Show project information
```

## Testing

The project includes comprehensive testing with multiple test types:

### Test Structure

```
tests/
├── test_cli.py              # CLI interface tests
├── test_utils.py            # Utility function tests
├── test_system.py           # System integration tests
├── test_execution.py        # Execution backend tests
├── test_integration.py      # Integration tests
├── test_benchmark.py        # Performance benchmarks
├── test_refactoring.py      # Legacy compatibility tests
├── core/
│   └── test_config.py       # Configuration tests
└── products/
    ├── gigapixel/
    │   └── test_api.py      # Gigapixel AI tests
    ├── video_ai/
    │   └── test_api.py      # Video AI tests
    └── photo_ai/
        └── test_api.py      # Photo AI tests
```

### Test Categories

Tests are organized with pytest markers:

- **`unit`**: Unit tests for individual components
- **`integration`**: Integration tests across components
- **`benchmark`**: Performance benchmarks

### Running Specific Test Types

```bash
# Run only unit tests
python -m pytest -m "unit"

# Run only integration tests
python -m pytest -m "integration"

# Run only benchmarks
python -m pytest -m "benchmark"

# Run tests with coverage
python -m pytest --cov=src/topyaz --cov-report=html
```

## CI/CD with GitHub Actions

The project uses GitHub Actions for automated CI/CD:

### Workflows

1. **Build & Test** (`.github/workflows/push.yml`)
   - Triggers on push to main branch and pull requests
   - Runs code quality checks (ruff, mypy)
   - Tests on multiple Python versions and platforms
   - Builds and verifies packages

2. **Release** (`.github/workflows/release.yml`)
   - Triggers on git tags matching `v*`
   - Runs comprehensive tests
   - Builds Python packages and binaries
   - Publishes to PyPI
   - Creates GitHub releases with assets

### Platform Support

CI/CD runs on:
- **Linux**: Ubuntu Latest
- **macOS**: macOS Latest  
- **Windows**: Windows Latest

With Python versions:
- Python 3.10
- Python 3.11
- Python 3.12

## Versioning

The project uses semantic versioning with git tags:

### Version Format

```
v<MAJOR>.<MINOR>.<PATCH>[-<PRERELEASE>][+<BUILD>]
```

Examples:
- `v1.0.0` - Release version
- `v1.0.0-alpha.1` - Pre-release version
- `v1.0.0+build.1` - Build metadata

### Creating Releases

1. **Create a git tag**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Or use the release script**:
   ```bash
   python scripts/release.py 1.0.0
   ```

3. **Or use make**:
   ```bash
   make tag VERSION=1.0.0
   make release VERSION=1.0.0
   ```

The GitHub Actions will automatically:
- Run tests
- Build packages and binaries
- Publish to PyPI
- Create GitHub release

## Binary Releases

The project automatically creates standalone binary executables for each platform:

### Binary Artifacts

- **Linux**: `topyaz-linux-x86_64.tar.gz`
- **macOS**: `topyaz-macos-x86_64.tar.gz`
- **Windows**: `topyaz-windows-x86_64.tar.gz`

### Binary Features

- Standalone executables (no Python installation required)
- All dependencies bundled
- Cross-platform compatibility
- Automatic testing during CI/CD

### Building Binaries Locally

```bash
# Build for current platform
python scripts/build_binary.py

# Build with all dependencies
python scripts/build_binary.py --install-deps --clean

# Build using spec file
python -m PyInstaller topyaz.spec
```

## Configuration

### Project Configuration

The build system is configured through:

- **`pyproject.toml`**: Python packaging and tool configuration
- **`topyaz.spec`**: PyInstaller specification for binary builds
- **`.github/workflows/`**: GitHub Actions workflows
- **`Makefile`**: Traditional make targets

### Environment Variables

The following environment variables can be used:

- **`TOPYAZ_*`**: Application configuration (see main docs)
- **`GITHUB_TOKEN`**: For GitHub API access
- **`PYPI_TOKEN`**: For PyPI publishing

## Development Workflow

### Typical Development Process

1. **Set up environment**:
   ```bash
   make install
   ```

2. **Make changes and test**:
   ```bash
   make test-coverage
   make lint
   ```

3. **Build and verify**:
   ```bash
   make build
   ```

4. **Run full CI pipeline**:
   ```bash
   make ci
   ```

5. **Create release**:
   ```bash
   make release VERSION=1.0.0
   ```

### Code Quality

The project enforces code quality through:

- **Ruff**: Linting and formatting
- **MyPy**: Type checking
- **Pytest**: Comprehensive testing
- **Coverage**: Code coverage reporting

### Pre-commit Hooks

The project supports pre-commit hooks for automatic code quality checks:

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Troubleshooting

### Common Issues

1. **Import errors in tests**:
   - Ensure package is installed: `make install`
   - Check Python path and virtual environment

2. **Binary build failures**:
   - Install PyInstaller: `pip install pyinstaller`
   - Check hidden imports in `topyaz.spec`

3. **Release failures**:
   - Check git tags and remote repository
   - Verify PyPI credentials and permissions

4. **CI/CD failures**:
   - Check GitHub Actions logs
   - Verify secrets and permissions

### Getting Help

- Check the main project documentation
- Review GitHub Actions logs for CI/CD issues
- Open an issue on the GitHub repository

## Contributing

To contribute to the build system:

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request

The CI/CD system will automatically test your changes across all supported platforms and Python versions.