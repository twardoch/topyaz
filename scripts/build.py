#!/usr/bin/env python3
# /// script
# dependencies = ["build", "hatchling", "hatch-vcs", "twine", "setuptools", "wheel"]
# ///
# this_file: scripts/build.py
"""
Comprehensive build script for topyaz package.

This script handles building Python packages (wheel and sdist) with proper
version management from git tags.
"""

import argparse
import os
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
    print("🧹 Cleaning previous build artifacts...")
    
    # Directories to clean
    dirs_to_clean = [
        project_root / "dist",
        project_root / "build",
        project_root / "*.egg-info",
        project_root / "__pycache__",
        project_root / ".pytest_cache",
        project_root / ".mypy_cache",
        project_root / ".ruff_cache",
    ]
    
    # Clean directories
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            if dir_path.is_dir():
                import shutil
                shutil.rmtree(dir_path)
                print(f"Removed directory: {dir_path}")
            else:
                dir_path.unlink()
                print(f"Removed file: {dir_path}")
    
    # Clean Python cache files
    for root, dirs, files in os.walk(project_root):
        for d in dirs[:]:  # Copy list to avoid modification during iteration
            if d == "__pycache__":
                import shutil
                shutil.rmtree(Path(root) / d)
                dirs.remove(d)
        for f in files:
            if f.endswith(('.pyc', '.pyo')):
                (Path(root) / f).unlink()


def check_git_status(project_root: Path) -> dict:
    """Check git status and version information."""
    print("🔍 Checking git status...")
    
    # Check if we're in a git repository
    try:
        result = run_command(["git", "rev-parse", "--git-dir"], cwd=project_root)
        print("✅ Git repository detected")
    except subprocess.CalledProcessError:
        print("❌ Not in a git repository")
        return {"error": "Not in a git repository"}
    
    # Get current commit
    commit = run_command(["git", "rev-parse", "HEAD"], cwd=project_root).stdout.strip()
    print(f"Current commit: {commit[:8]}")
    
    # Check for uncommitted changes
    status = run_command(["git", "status", "--porcelain"], cwd=project_root).stdout.strip()
    if status:
        print("⚠️  Uncommitted changes detected:")
        print(status)
    else:
        print("✅ Working directory clean")
    
    # Get version from git
    try:
        version = run_command(["git", "describe", "--tags", "--always"], cwd=project_root).stdout.strip()
        print(f"Version: {version}")
    except subprocess.CalledProcessError:
        version = "0.0.0-dev"
        print(f"No tags found, using: {version}")
    
    # Check if current commit is tagged
    try:
        exact_tag = run_command(["git", "describe", "--exact-match", "--tags", "HEAD"], cwd=project_root).stdout.strip()
        print(f"✅ Current commit is tagged: {exact_tag}")
        is_tagged = True
    except subprocess.CalledProcessError:
        print("ℹ️  Current commit is not tagged")
        is_tagged = False
    
    return {
        "commit": commit,
        "version": version,
        "is_tagged": is_tagged,
        "has_changes": bool(status),
        "status": status
    }


def build_package(project_root: Path, build_type: str = "both") -> None:
    """Build the package using python -m build."""
    print(f"🏗️  Building package ({build_type})...")
    
    # Ensure dist directory exists
    dist_dir = project_root / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    # Build command
    cmd = [sys.executable, "-m", "build"]
    
    if build_type == "wheel":
        cmd.append("--wheel")
    elif build_type == "sdist":
        cmd.append("--sdist")
    elif build_type == "both":
        cmd.extend(["--wheel", "--sdist"])
    else:
        raise ValueError(f"Invalid build_type: {build_type}")
    
    # Add output directory
    cmd.extend(["--outdir", str(dist_dir)])
    
    # Run build
    try:
        run_command(cmd, cwd=project_root)
        print("✅ Package built successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)


def verify_build_artifacts(project_root: Path) -> dict:
    """Verify the built artifacts."""
    print("🔍 Verifying build artifacts...")
    
    dist_dir = project_root / "dist"
    if not dist_dir.exists():
        print("❌ Dist directory not found")
        return {"error": "Dist directory not found"}
    
    # Find artifacts
    wheels = list(dist_dir.glob("*.whl"))
    sdists = list(dist_dir.glob("*.tar.gz"))
    
    print(f"Found {len(wheels)} wheel(s) and {len(sdists)} source distribution(s)")
    
    artifacts = {
        "wheels": wheels,
        "sdists": sdists,
        "total": len(wheels) + len(sdists)
    }
    
    # Display artifacts
    for wheel in wheels:
        print(f"  📦 Wheel: {wheel.name} ({wheel.stat().st_size} bytes)")
    
    for sdist in sdists:
        print(f"  📦 Source: {sdist.name} ({sdist.stat().st_size} bytes)")
    
    # Basic verification
    if not wheels and not sdists:
        print("❌ No artifacts found")
        return {"error": "No artifacts found"}
    
    print("✅ Build artifacts verified")
    return artifacts


def check_package_metadata(project_root: Path) -> None:
    """Check package metadata using twine."""
    print("🔍 Checking package metadata...")
    
    dist_dir = project_root / "dist"
    artifacts = list(dist_dir.glob("*"))
    
    if not artifacts:
        print("❌ No artifacts to check")
        return
    
    try:
        cmd = [sys.executable, "-m", "twine", "check"] + [str(a) for a in artifacts]
        run_command(cmd, cwd=project_root)
        print("✅ Package metadata is valid")
    except subprocess.CalledProcessError as e:
        print(f"❌ Package metadata check failed: {e}")
        sys.exit(1)


def main():
    """Main build script."""
    parser = argparse.ArgumentParser(description="Build topyaz package")
    parser.add_argument(
        "--type", 
        choices=["wheel", "sdist", "both"],
        default="both",
        help="Type of build to perform"
    )
    parser.add_argument(
        "--clean", 
        action="store_true",
        help="Clean build artifacts before building"
    )
    parser.add_argument(
        "--check", 
        action="store_true",
        help="Check package metadata after building"
    )
    parser.add_argument(
        "--no-verify", 
        action="store_true",
        help="Skip verification of build artifacts"
    )
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent.parent
    print(f"Project root: {project_root}")
    
    # Clean if requested
    if args.clean:
        clean_build_artifacts(project_root)
    
    # Check git status
    git_info = check_git_status(project_root)
    if "error" in git_info:
        print(f"❌ Git check failed: {git_info['error']}")
        sys.exit(1)
    
    # Build package
    build_package(project_root, args.type)
    
    # Verify artifacts
    if not args.no_verify:
        artifacts = verify_build_artifacts(project_root)
        if "error" in artifacts:
            print(f"❌ Verification failed: {artifacts['error']}")
            sys.exit(1)
    
    # Check package metadata
    if args.check:
        check_package_metadata(project_root)
    
    print("✅ Build completed successfully!")
    print(f"Artifacts available in: {project_root / 'dist'}")


if __name__ == "__main__":
    main()