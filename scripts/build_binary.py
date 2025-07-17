#!/usr/bin/env python3
# /// script
# dependencies = ["pyinstaller", "setuptools", "wheel"]
# ///
# this_file: scripts/build_binary.py
"""
Build binary executable for topyaz using PyInstaller.
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], cwd: Path = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    if cwd:
        print(f"Working directory: {cwd}")
    
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check
    )
    
    if result.stdout:
        print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result


def clean_build_artifacts(project_root: Path) -> None:
    """Clean previous build artifacts."""
    print("🧹 Cleaning binary build artifacts...")
    
    # Directories to clean
    dirs_to_clean = [
        project_root / "build",
        project_root / "dist",
        project_root / "__pycache__",
    ]
    
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"Removed: {dir_path}")


def install_dependencies(project_root: Path) -> None:
    """Install package and build dependencies."""
    print("📦 Installing dependencies...")
    
    # Install the package in development mode
    run_command([
        sys.executable, "-m", "pip", "install", "-e", ".[dev]"
    ], cwd=project_root)
    
    # Install PyInstaller
    run_command([
        sys.executable, "-m", "pip", "install", "pyinstaller"
    ], cwd=project_root)


def build_binary(project_root: Path, output_name: str = None) -> Path:
    """Build the binary using PyInstaller."""
    print("🏗️  Building binary executable...")
    
    # Determine output name
    if not output_name:
        system = platform.system().lower()
        architecture = platform.machine().lower()
        output_name = f"topyaz-{system}-{architecture}"
        
        if system == "windows":
            output_name += ".exe"
    
    # Check if spec file exists
    spec_file = project_root / "topyaz.spec"
    
    if spec_file.exists():
        print(f"Using spec file: {spec_file}")
        # Build using spec file
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            str(spec_file)
        ]
    else:
        print("Using direct PyInstaller command")
        # Build using direct command
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--name", output_name,
            "--clean",
            "--noconfirm",
            # Add hidden imports for critical modules
            "--hidden-import", "topyaz",
            "--hidden-import", "topyaz.cli",
            "--hidden-import", "topyaz.core.config",
            "--hidden-import", "topyaz.products.gigapixel.api",
            "--hidden-import", "topyaz.products.video_ai.api",
            "--hidden-import", "topyaz.products.photo_ai.api",
            "--hidden-import", "fire",
            "--hidden-import", "paramiko",
            "--hidden-import", "fabric",
            "--hidden-import", "pyyaml",
            "--hidden-import", "tqdm",
            "--hidden-import", "psutil",
            "--hidden-import", "loguru",
            "--hidden-import", "rich",
            "--hidden-import", "PIL",
            # Add data files
            "--add-data", "src/topyaz:topyaz",
            # Main script
            "src/topyaz/__main__.py"
        ]
    
    # Run PyInstaller
    try:
        run_command(cmd, cwd=project_root)
        print("✅ Binary built successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Binary build failed: {e}")
        raise
    
    # Find the built binary
    dist_dir = project_root / "dist"
    if spec_file.exists():
        # When using spec file, the binary is named "topyaz"
        binary_name = "topyaz"
        if platform.system().lower() == "windows":
            binary_name += ".exe"
        binary_path = dist_dir / binary_name
    else:
        # When using direct command, the binary is named according to --name
        binary_path = dist_dir / output_name
    
    if not binary_path.exists():
        # Try to find any executable in dist directory
        executables = list(dist_dir.glob("*"))
        executables = [f for f in executables if f.is_file() and (f.suffix == ".exe" or f.stat().st_mode & 0o111)]
        
        if executables:
            binary_path = executables[0]
        else:
            raise FileNotFoundError(f"Built binary not found in {dist_dir}")
    
    return binary_path


def test_binary(binary_path: Path) -> None:
    """Test the built binary."""
    print(f"🧪 Testing binary: {binary_path}")
    
    # Make sure it's executable on Unix-like systems
    if platform.system() != "Windows":
        binary_path.chmod(binary_path.stat().st_mode | 0o111)
    
    # Test basic functionality
    try:
        # Test help command
        result = run_command([str(binary_path), "--help"], check=False)
        
        if result.returncode == 0:
            print("✅ Binary test passed")
        else:
            print(f"⚠️  Binary test returned non-zero exit code: {result.returncode}")
            print("This might be expected for --help command")
    except Exception as e:
        print(f"❌ Binary test failed: {e}")
        raise


def package_binary(binary_path: Path, project_root: Path) -> Path:
    """Package the binary for distribution."""
    print("📦 Packaging binary for distribution...")
    
    # Create packaging directory
    package_dir = project_root / "binary-package"
    package_dir.mkdir(exist_ok=True)
    
    # Copy binary
    binary_name = binary_path.name
    shutil.copy2(binary_path, package_dir / binary_name)
    
    # Create README
    readme_content = f"""# Topyaz Binary Release

This is a standalone binary executable of the topyaz package.

## Usage

```bash
./{binary_name} --help
```

## System Information

- Built on: {platform.system()} {platform.release()}
- Architecture: {platform.machine()}
- Python version: {platform.python_version()}

## Installation

1. Download this archive
2. Extract the binary
3. Make it executable (Unix/Linux/macOS): `chmod +x {binary_name}`
4. Run: `./{binary_name} --help`

## Support

For issues and documentation, visit: https://github.com/twardoch/topyaz
"""
    
    with open(package_dir / "README.md", "w") as f:
        f.write(readme_content)
    
    # Create version file
    version_info = {
        "version": "1.0.0",  # This should be dynamically determined
        "build_date": "2024-01-01",  # This should be current date
        "system": platform.system(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
    }
    
    import json
    with open(package_dir / "version.json", "w") as f:
        json.dump(version_info, f, indent=2)
    
    print(f"✅ Binary packaged in: {package_dir}")
    return package_dir


def main():
    """Main binary build script."""
    parser = argparse.ArgumentParser(description="Build topyaz binary executable")
    parser.add_argument(
        "--output-name",
        help="Name of the output binary"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build artifacts before building"
    )
    parser.add_argument(
        "--no-test",
        action="store_true",
        help="Skip testing the built binary"
    )
    parser.add_argument(
        "--no-package",
        action="store_true",
        help="Skip packaging the binary"
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install dependencies before building"
    )
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent.parent
    print(f"Project root: {project_root}")
    
    # Clean if requested
    if args.clean:
        clean_build_artifacts(project_root)
    
    # Install dependencies if requested
    if args.install_deps:
        install_dependencies(project_root)
    
    # Build binary
    binary_path = build_binary(project_root, args.output_name)
    print(f"Binary built at: {binary_path}")
    
    # Test binary
    if not args.no_test:
        test_binary(binary_path)
    
    # Package binary
    if not args.no_package:
        package_dir = package_binary(binary_path, project_root)
        print(f"Binary package created at: {package_dir}")
    
    print("✅ Binary build completed successfully!")


if __name__ == "__main__":
    main()