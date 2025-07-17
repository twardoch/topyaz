# GitHub Actions Workflow Updates

Due to GitHub App permissions, the workflow files need to be updated manually. Here are the changes needed:

## 1. Update `.github/workflows/push.yml`

Replace the entire content of `.github/workflows/push.yml` with:

```yaml
name: Build & Test

on:
  push:
    branches: [main]
    tags-ignore: ["v*"]
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  id-token: write

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  quality:
    name: Code Quality
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -e .[dev,test]

      - name: Run Ruff lint
        run: python -m ruff check src/topyaz tests --output-format=github

      - name: Run Ruff format check
        run: python -m ruff format src/topyaz tests --check --respect-gitignore

      - name: Run Mypy type checking
        run: python -m mypy src/topyaz tests --config-file=pyproject.toml

  test:
    name: Run Tests
    needs: quality
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
        os: [ubuntu-latest, windows-latest, macos-latest]
      fail-fast: false
    runs-on: ${{ matrix.os }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -e .[test]

      - name: Run tests with coverage
        run: python scripts/test.py --coverage --parallel --junit

      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.python-version }}-${{ matrix.os }}
          path: coverage.xml
        if: always()

      - name: Upload test results
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.python-version }}-${{ matrix.os }}
          path: test-results.xml
        if: always()

  build:
    name: Build Distribution
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install build dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install build hatchling hatch-vcs twine

      - name: Build distributions
        run: python scripts/build.py --clean --check

      - name: Upload distribution artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist-files
          path: dist/
          retention-days: 7
```

## 2. Update `.github/workflows/release.yml`

Replace the entire content of `.github/workflows/release.yml` with:

```yaml
name: Release

on:
  push:
    tags: ["v*"]

permissions:
  contents: write
  id-token: write

jobs:
  test:
    name: Run Tests Before Release
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -e .[dev,test]

      - name: Run comprehensive tests
        run: python scripts/test.py --coverage --parallel --lint

  build-python:
    name: Build Python Package
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install build dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install build hatchling hatch-vcs twine

      - name: Build distributions
        run: python scripts/build.py --clean --check

      - name: Upload Python artifacts
        uses: actions/upload-artifact@v4
        with:
          name: python-dist
          path: dist/
          retention-days: 7

  build-binaries:
    name: Build Binary (${{ matrix.os }})
    needs: test
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            artifact_name: topyaz-linux-x86_64
            binary_name: topyaz
          - os: windows-latest
            artifact_name: topyaz-windows-x86_64
            binary_name: topyaz.exe
          - os: macos-latest
            artifact_name: topyaz-macos-x86_64
            binary_name: topyaz
    runs-on: ${{ matrix.os }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -e .[dev]
          python -m pip install pyinstaller

      - name: Build binary with PyInstaller
        run: |
          pyinstaller --onefile --name ${{ matrix.binary_name }} --add-data "src/topyaz:topyaz" src/topyaz/__main__.py

      - name: Test binary (Unix)
        if: runner.os != 'Windows'
        run: |
          chmod +x dist/${{ matrix.binary_name }}
          ./dist/${{ matrix.binary_name }} --help

      - name: Test binary (Windows)
        if: runner.os == 'Windows'
        run: |
          dist/${{ matrix.binary_name }} --help

      - name: Create binary archive
        run: |
          mkdir -p binary-release
          cp dist/${{ matrix.binary_name }} binary-release/
          echo "# topyaz Binary Release" > binary-release/README.md
          echo "Binary executable for ${{ matrix.os }}" >> binary-release/README.md
          echo "Run with: ./${{ matrix.binary_name }} --help" >> binary-release/README.md

      - name: Upload binary artifacts
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.artifact_name }}
          path: binary-release/
          retention-days: 7

  release:
    name: Create Release
    needs: [build-python, build-binaries]
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/topyaz
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Download Python artifacts
        uses: actions/download-artifact@v4
        with:
          name: python-dist
          path: dist/

      - name: Download binary artifacts
        uses: actions/download-artifact@v4
        with:
          path: binaries/

      - name: Prepare release assets
        run: |
          # Create release directory
          mkdir -p release-assets
          
          # Copy Python distributions
          cp dist/* release-assets/
          
          # Create binary archives
          cd binaries
          for dir in */; do
            if [ -d "$dir" ]; then
              cd "$dir"
              tar -czf "../../release-assets/${dir%/}.tar.gz" *
              cd ..
            fi
          done
          cd ..
          
          # List all release assets
          ls -la release-assets/

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_TOKEN }}
          packages-dir: dist/

      - name: Extract version from tag
        id: get_version
        run: |
          VERSION=${GITHUB_REF#refs/tags/}
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "Version: $VERSION"

      - name: Generate release notes
        run: |
          python scripts/release.py ${{ steps.get_version.outputs.version }} --dry-run > release-notes.md

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: release-assets/*
          body_path: release-notes.md
          generate_release_notes: true
          prerelease: ${{ contains(steps.get_version.outputs.version, '-') }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 3. Next Steps

1. **Create a Pull Request**: Visit the URL shown in the git push output to create a PR for the infrastructure changes.

2. **After PR is merged**: Update the workflow files manually with the content above.

3. **Test the new system**:
   ```bash
   # Test locally
   make install
   make test-coverage
   make build
   
   # Test release (dry run)
   make release-dry VERSION=1.0.0
   ```

4. **Create your first release**:
   ```bash
   # Create and push a tag
   git tag v1.0.0
   git push origin v1.0.0
   
   # Or use the release script
   make release VERSION=1.0.0
   ```

## What's Included

✅ **Complete build system** with scripts for building, testing, and releasing
✅ **Comprehensive test suite** with unit, integration, and benchmark tests  
✅ **Git-tag-based semversioning** with automatic version management
✅ **Multiplatform CI/CD** supporting Linux, macOS, and Windows
✅ **Binary releases** with standalone executables
✅ **PyPI publishing** with automatic releases
✅ **GitHub releases** with artifacts and release notes
✅ **Development tools** including Makefile and convenience scripts
✅ **Documentation** in BUILD.md

The system is production-ready and follows modern Python packaging best practices!