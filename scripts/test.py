#!/usr/bin/env python3
# /// script
# dependencies = ["pytest", "pytest-cov", "pytest-xdist", "pytest-benchmark", "pytest-asyncio", "coverage"]
# ///
# this_file: scripts/test.py
"""
Comprehensive test script for topyaz package.

This script runs tests with various options including coverage, parallel execution,
and benchmarks.
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


def install_package(project_root: Path, editable: bool = True) -> None:
    """Install the package in development mode."""
    print("📦 Installing package...")
    
    cmd = [sys.executable, "-m", "pip", "install"]
    
    if editable:
        cmd.append("-e")
    
    cmd.append(f"{project_root}[test]")
    
    try:
        run_command(cmd, cwd=project_root)
        print("✅ Package installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Package installation failed: {e}")
        sys.exit(1)


def run_tests(
    project_root: Path,
    test_path: str = "tests",
    coverage: bool = False,
    parallel: bool = False,
    verbose: bool = False,
    markers: str = None,
    benchmark: bool = False,
    junit: bool = False,
    maxfail: int = None,
    timeout: int = None
) -> dict:
    """Run tests with specified options."""
    print("🧪 Running tests...")
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add test path
    cmd.append(test_path)
    
    # Verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("--tb=short")
    
    # Parallel execution
    if parallel:
        cmd.extend(["-n", "auto"])
    
    # Coverage
    if coverage:
        cmd.extend([
            "--cov=src/topyaz",
            "--cov=tests",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-config=pyproject.toml"
        ])
    
    # Markers
    if markers:
        cmd.extend(["-m", markers])
    
    # Benchmark
    if benchmark:
        cmd.append("--benchmark-only")
    
    # JUnit XML output
    if junit:
        cmd.extend(["--junit-xml=test-results.xml"])
    
    # Max failures
    if maxfail:
        cmd.extend(["--maxfail", str(maxfail)])
    
    # Timeout
    if timeout:
        cmd.extend(["--timeout", str(timeout)])
    
    # Additional options
    cmd.extend([
        "--disable-warnings",
        "--durations=10"
    ])
    
    # Run tests
    try:
        result = run_command(cmd, cwd=project_root, check=False)
        
        # Parse results
        test_results = {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print(f"❌ Tests failed (exit code: {result.returncode})")
        
        return test_results
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Test execution failed: {e}")
        return {
            "returncode": e.returncode,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "success": False
        }


def run_linting(project_root: Path) -> dict:
    """Run code linting and formatting checks."""
    print("🔍 Running linting checks...")
    
    results = {}
    
    # Ruff linting
    try:
        print("Running ruff check...")
        result = run_command([
            sys.executable, "-m", "ruff", "check", 
            "src/topyaz", "tests", "--output-format=text"
        ], cwd=project_root, check=False)
        results["ruff_check"] = result.returncode == 0
        if result.returncode != 0:
            print("❌ Ruff linting failed")
        else:
            print("✅ Ruff linting passed")
    except subprocess.CalledProcessError:
        results["ruff_check"] = False
        print("❌ Ruff check failed to run")
    
    # Ruff formatting
    try:
        print("Running ruff format check...")
        result = run_command([
            sys.executable, "-m", "ruff", "format", 
            "src/topyaz", "tests", "--check", "--respect-gitignore"
        ], cwd=project_root, check=False)
        results["ruff_format"] = result.returncode == 0
        if result.returncode != 0:
            print("❌ Ruff formatting check failed")
        else:
            print("✅ Ruff formatting check passed")
    except subprocess.CalledProcessError:
        results["ruff_format"] = False
        print("❌ Ruff format check failed to run")
    
    # Mypy type checking
    try:
        print("Running mypy type checking...")
        result = run_command([
            sys.executable, "-m", "mypy", 
            "src/topyaz", "tests", "--config-file=pyproject.toml"
        ], cwd=project_root, check=False)
        results["mypy"] = result.returncode == 0
        if result.returncode != 0:
            print("❌ Mypy type checking failed")
        else:
            print("✅ Mypy type checking passed")
    except subprocess.CalledProcessError:
        results["mypy"] = False
        print("❌ Mypy failed to run")
    
    return results


def generate_coverage_report(project_root: Path) -> None:
    """Generate coverage report."""
    print("📊 Generating coverage report...")
    
    # Check if coverage data exists
    coverage_file = project_root / ".coverage"
    if not coverage_file.exists():
        print("❌ No coverage data found")
        return
    
    try:
        # Generate terminal report
        run_command([
            sys.executable, "-m", "coverage", "report", "--show-missing"
        ], cwd=project_root)
        
        # Generate HTML report
        run_command([
            sys.executable, "-m", "coverage", "html"
        ], cwd=project_root)
        
        # Generate XML report
        run_command([
            sys.executable, "-m", "coverage", "xml"
        ], cwd=project_root)
        
        print("✅ Coverage reports generated")
        print(f"  HTML report: {project_root / 'htmlcov' / 'index.html'}")
        print(f"  XML report: {project_root / 'coverage.xml'}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Coverage report generation failed: {e}")


def main():
    """Main test script."""
    parser = argparse.ArgumentParser(description="Run topyaz tests")
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage reporting"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--markers",
        type=str,
        help="Run tests with specific markers (e.g., 'unit', 'integration', 'benchmark')"
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run only benchmark tests"
    )
    parser.add_argument(
        "--junit",
        action="store_true",
        help="Generate JUnit XML report"
    )
    parser.add_argument(
        "--maxfail",
        type=int,
        help="Stop after N failures"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        help="Timeout for individual tests (seconds)"
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run linting checks"
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install package before running tests"
    )
    parser.add_argument(
        "--test-path",
        type=str,
        default="tests",
        help="Path to test directory"
    )
    parser.add_argument(
        "--no-install",
        action="store_true",
        help="Skip package installation"
    )
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent.parent
    print(f"Project root: {project_root}")
    
    # Change to project root
    os.chdir(project_root)
    
    # Install package if requested or by default
    if args.install or not args.no_install:
        install_package(project_root)
    
    # Run linting if requested
    if args.lint:
        lint_results = run_linting(project_root)
        if not all(lint_results.values()):
            print("❌ Linting checks failed")
            sys.exit(1)
    
    # Run tests
    test_results = run_tests(
        project_root=project_root,
        test_path=args.test_path,
        coverage=args.coverage,
        parallel=args.parallel,
        verbose=args.verbose,
        markers=args.markers,
        benchmark=args.benchmark,
        junit=args.junit,
        maxfail=args.maxfail,
        timeout=args.timeout
    )
    
    # Generate coverage report if coverage was requested
    if args.coverage:
        generate_coverage_report(project_root)
    
    # Exit with test result code
    if not test_results["success"]:
        sys.exit(test_results["returncode"])
    
    print("✅ All tests completed successfully!")


if __name__ == "__main__":
    main()