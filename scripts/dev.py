#!/usr/bin/env python3
# /// script
# dependencies = ["build", "hatchling", "hatch-vcs", "twine", "setuptools", "wheel", "pytest", "pytest-cov", "pytest-xdist", "pytest-benchmark"]
# ///
# this_file: scripts/dev.py
"""
Development convenience script for topyaz package.

This script provides common development tasks in a single interface.
"""

import argparse
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


def cmd_test(args, project_root: Path) -> None:
    """Run tests."""
    test_script = project_root / "scripts" / "test.py"
    
    cmd = [sys.executable, str(test_script)]
    
    if args.coverage:
        cmd.append("--coverage")
    if args.parallel:
        cmd.append("--parallel")
    if args.verbose:
        cmd.append("--verbose")
    if args.lint:
        cmd.append("--lint")
    if args.benchmark:
        cmd.append("--benchmark")
    
    subprocess.run(cmd, cwd=project_root)


def cmd_build(args, project_root: Path) -> None:
    """Build package."""
    build_script = project_root / "scripts" / "build.py"
    
    cmd = [sys.executable, str(build_script)]
    
    if args.clean:
        cmd.append("--clean")
    if args.check:
        cmd.append("--check")
    
    subprocess.run(cmd, cwd=project_root)


def cmd_release(args, project_root: Path) -> None:
    """Release package."""
    release_script = project_root / "scripts" / "release.py"
    
    cmd = [sys.executable, str(release_script), args.version]
    
    if args.dry_run:
        cmd.append("--dry-run")
    if args.repository:
        cmd.extend(["--repository", args.repository])
    
    subprocess.run(cmd, cwd=project_root)


def cmd_lint(args, project_root: Path) -> None:
    """Run linting and formatting."""
    print("🔍 Running linting and formatting...")
    
    # Ruff check
    try:
        run_command([
            sys.executable, "-m", "ruff", "check", 
            "src/topyaz", "tests"
        ], cwd=project_root)
        print("✅ Ruff check passed")
    except subprocess.CalledProcessError:
        print("❌ Ruff check failed")
        if not args.fix:
            return
    
    # Ruff format
    try:
        format_cmd = [
            sys.executable, "-m", "ruff", "format", 
            "src/topyaz", "tests", "--respect-gitignore"
        ]
        if not args.fix:
            format_cmd.append("--check")
        
        run_command(format_cmd, cwd=project_root)
        print("✅ Ruff format passed")
    except subprocess.CalledProcessError:
        print("❌ Ruff format failed")
        if not args.fix:
            return
    
    # Mypy type checking
    try:
        run_command([
            sys.executable, "-m", "mypy", 
            "src/topyaz", "tests", "--config-file=pyproject.toml"
        ], cwd=project_root)
        print("✅ Mypy type checking passed")
    except subprocess.CalledProcessError:
        print("❌ Mypy type checking failed")


def cmd_install(args, project_root: Path) -> None:
    """Install package in development mode."""
    print("📦 Installing package in development mode...")
    
    cmd = [sys.executable, "-m", "pip", "install", "-e", f"{project_root}[dev,test]"]
    
    if args.force:
        cmd.append("--force-reinstall")
    
    subprocess.run(cmd, cwd=project_root)


def cmd_clean(args, project_root: Path) -> None:
    """Clean build artifacts."""
    print("🧹 Cleaning build artifacts...")
    
    import os
    import shutil
    
    # Directories to clean
    dirs_to_clean = [
        "dist",
        "build",
        "*.egg-info",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "htmlcov",
    ]
    
    for dir_name in dirs_to_clean:
        dir_path = project_root / dir_name
        if dir_path.exists():
            if dir_path.is_dir():
                shutil.rmtree(dir_path)
                print(f"Removed: {dir_path}")
            else:
                dir_path.unlink()
                print(f"Removed: {dir_path}")
    
    # Clean Python cache files
    for root, dirs, files in os.walk(project_root):
        for d in dirs[:]:
            if d == "__pycache__":
                shutil.rmtree(Path(root) / d)
                dirs.remove(d)
        for f in files:
            if f.endswith(('.pyc', '.pyo')):
                (Path(root) / f).unlink()
    
    print("✅ Clean completed")


def cmd_ci(args, project_root: Path) -> None:
    """Run CI pipeline locally."""
    print("🔄 Running CI pipeline locally...")
    
    # Step 1: Install
    cmd_install(args, project_root)
    
    # Step 2: Lint
    cmd_lint(args, project_root)
    
    # Step 3: Test with coverage
    test_args = argparse.Namespace(
        coverage=True,
        parallel=True,
        verbose=True,
        lint=False,
        benchmark=False
    )
    cmd_test(test_args, project_root)
    
    # Step 4: Build
    build_args = argparse.Namespace(
        clean=True,
        check=True
    )
    cmd_build(build_args, project_root)
    
    print("✅ CI pipeline completed successfully!")


def main():
    """Main development script."""
    parser = argparse.ArgumentParser(description="Development tools for topyaz")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--coverage", action="store_true", help="Run with coverage")
    test_parser.add_argument("--parallel", action="store_true", help="Run in parallel")
    test_parser.add_argument("--verbose", action="store_true", help="Verbose output")
    test_parser.add_argument("--lint", action="store_true", help="Run linting")
    test_parser.add_argument("--benchmark", action="store_true", help="Run benchmarks")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build package")
    build_parser.add_argument("--clean", action="store_true", help="Clean before build")
    build_parser.add_argument("--check", action="store_true", help="Check metadata")
    
    # Release command
    release_parser = subparsers.add_parser("release", help="Release package")
    release_parser.add_argument("version", help="Version to release")
    release_parser.add_argument("--dry-run", action="store_true", help="Dry run")
    release_parser.add_argument("--repository", help="Repository to publish to")
    
    # Lint command
    lint_parser = subparsers.add_parser("lint", help="Run linting")
    lint_parser.add_argument("--fix", action="store_true", help="Fix issues")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install package")
    install_parser.add_argument("--force", action="store_true", help="Force reinstall")
    
    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean build artifacts")
    
    # CI command
    ci_parser = subparsers.add_parser("ci", help="Run CI pipeline locally")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Get project root
    project_root = Path(__file__).parent.parent
    print(f"Project root: {project_root}")
    
    # Route to appropriate command
    if args.command == "test":
        cmd_test(args, project_root)
    elif args.command == "build":
        cmd_build(args, project_root)
    elif args.command == "release":
        cmd_release(args, project_root)
    elif args.command == "lint":
        cmd_lint(args, project_root)
    elif args.command == "install":
        cmd_install(args, project_root)
    elif args.command == "clean":
        cmd_clean(args, project_root)
    elif args.command == "ci":
        cmd_ci(args, project_root)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()