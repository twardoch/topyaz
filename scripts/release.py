#!/usr/bin/env python3
# /// script
# dependencies = ["build", "hatchling", "hatch-vcs", "twine", "setuptools", "wheel", "requests"]
# ///
# this_file: scripts/release.py
"""
Comprehensive release script for topyaz package.

This script handles the complete release process including:
- Version validation
- Building packages
- Publishing to PyPI
- Creating GitHub releases
- Generating release notes
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List


def run_command(cmd: List[str], cwd: Path = None, check: bool = True) -> subprocess.CompletedProcess:
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


def validate_version(version: str) -> bool:
    """Validate that version follows semantic versioning."""
    # Semantic versioning pattern: MAJOR.MINOR.PATCH with optional pre-release and build metadata
    semver_pattern = r'^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
    
    if re.match(semver_pattern, version):
        print(f"✅ Version {version} is valid semantic version")
        return True
    else:
        print(f"❌ Version {version} is not a valid semantic version")
        return False


def get_git_info(project_root: Path) -> Dict:
    """Get git information for release."""
    print("🔍 Getting git information...")
    
    # Check if we're in a git repository
    try:
        run_command(["git", "rev-parse", "--git-dir"], cwd=project_root)
    except subprocess.CalledProcessError:
        raise RuntimeError("Not in a git repository")
    
    # Get current commit
    commit = run_command(["git", "rev-parse", "HEAD"], cwd=project_root).stdout.strip()
    
    # Get current branch
    branch = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=project_root).stdout.strip()
    
    # Check for uncommitted changes
    status = run_command(["git", "status", "--porcelain"], cwd=project_root).stdout.strip()
    
    # Get latest tag
    try:
        latest_tag = run_command(["git", "describe", "--tags", "--abbrev=0"], cwd=project_root).stdout.strip()
    except subprocess.CalledProcessError:
        latest_tag = None
    
    # Check if current commit is tagged
    try:
        current_tag = run_command(["git", "describe", "--exact-match", "--tags", "HEAD"], cwd=project_root).stdout.strip()
    except subprocess.CalledProcessError:
        current_tag = None
    
    return {
        "commit": commit,
        "branch": branch,
        "has_changes": bool(status),
        "status": status,
        "latest_tag": latest_tag,
        "current_tag": current_tag
    }


def create_git_tag(project_root: Path, version: str, message: str = None) -> None:
    """Create a git tag for the release."""
    print(f"🏷️  Creating git tag {version}...")
    
    # Ensure version starts with 'v'
    if not version.startswith('v'):
        version = f"v{version}"
    
    # Create tag command
    cmd = ["git", "tag", "-a", version]
    
    if message:
        cmd.extend(["-m", message])
    else:
        cmd.extend(["-m", f"Release {version}"])
    
    try:
        run_command(cmd, cwd=project_root)
        print(f"✅ Tag {version} created successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create tag: {e}")
        raise


def generate_release_notes(project_root: Path, version: str, previous_version: str = None) -> str:
    """Generate release notes from git commits."""
    print("📝 Generating release notes...")
    
    # Get commits since last release
    if previous_version:
        commit_range = f"{previous_version}..HEAD"
    else:
        commit_range = "HEAD"
    
    try:
        result = run_command([
            "git", "log", commit_range, 
            "--pretty=format:- %s (%h)", 
            "--no-merges"
        ], cwd=project_root)
        
        commits = result.stdout.strip().split('\n')
        
        # Filter and categorize commits
        features = []
        fixes = []
        docs = []
        others = []
        
        for commit in commits:
            if not commit.strip():
                continue
                
            commit_lower = commit.lower()
            if any(word in commit_lower for word in ['feat:', 'feature:', 'add:', 'implement:']):
                features.append(commit)
            elif any(word in commit_lower for word in ['fix:', 'bug:', 'patch:', 'resolve:']):
                fixes.append(commit)
            elif any(word in commit_lower for word in ['doc:', 'docs:', 'documentation:']):
                docs.append(commit)
            else:
                others.append(commit)
        
        # Generate release notes
        release_notes = f"# Release {version}\n\n"
        
        if features:
            release_notes += "## 🚀 Features\n\n"
            release_notes += '\n'.join(features) + '\n\n'
        
        if fixes:
            release_notes += "## 🐛 Bug Fixes\n\n"
            release_notes += '\n'.join(fixes) + '\n\n'
        
        if docs:
            release_notes += "## 📚 Documentation\n\n"
            release_notes += '\n'.join(docs) + '\n\n'
        
        if others:
            release_notes += "## 🔧 Other Changes\n\n"
            release_notes += '\n'.join(others) + '\n\n'
        
        # Add installation instructions
        release_notes += "## 📦 Installation\n\n"
        release_notes += f"```bash\npip install topyaz=={version.lstrip('v')}\n```\n\n"
        
        # Add full changelog link
        if previous_version:
            release_notes += f"**Full Changelog**: https://github.com/twardoch/topyaz/compare/{previous_version}...{version}\n"
        
        print("✅ Release notes generated")
        return release_notes
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate release notes: {e}")
        return f"# Release {version}\n\nRelease notes could not be generated automatically."


def build_package(project_root: Path) -> List[Path]:
    """Build the package and return list of artifacts."""
    print("🏗️  Building package...")
    
    # Import and run build script
    build_script = project_root / "scripts" / "build.py"
    
    try:
        run_command([
            sys.executable, str(build_script),
            "--type", "both",
            "--clean",
            "--check"
        ], cwd=project_root)
        
        # Find built artifacts
        dist_dir = project_root / "dist"
        artifacts = list(dist_dir.glob("*"))
        
        print(f"✅ Built {len(artifacts)} artifacts")
        return artifacts
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        raise


def publish_to_pypi(project_root: Path, repository: str = "pypi", dry_run: bool = False) -> None:
    """Publish package to PyPI."""
    if dry_run:
        print("🧪 Dry run: Would publish to PyPI")
        return
    
    print(f"🚀 Publishing to {repository}...")
    
    dist_dir = project_root / "dist"
    artifacts = list(dist_dir.glob("*"))
    
    if not artifacts:
        raise RuntimeError("No artifacts found to publish")
    
    # Build twine command
    cmd = [sys.executable, "-m", "twine", "upload"]
    
    if repository == "testpypi":
        cmd.extend(["--repository", "testpypi"])
    
    # Add artifacts
    cmd.extend(str(a) for a in artifacts)
    
    try:
        run_command(cmd, cwd=project_root)
        print(f"✅ Published to {repository}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Publication failed: {e}")
        raise


def create_github_release(
    project_root: Path,
    version: str,
    release_notes: str,
    artifacts: List[Path],
    dry_run: bool = False
) -> None:
    """Create GitHub release."""
    if dry_run:
        print("🧪 Dry run: Would create GitHub release")
        return
    
    print("🐙 Creating GitHub release...")
    
    # Check if gh CLI is available
    try:
        run_command(["gh", "--version"], cwd=project_root)
    except subprocess.CalledProcessError:
        print("❌ GitHub CLI (gh) not found, skipping GitHub release")
        return
    
    # Write release notes to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(release_notes)
        notes_file = f.name
    
    try:
        # Create release
        cmd = [
            "gh", "release", "create", version,
            "--title", f"Release {version}",
            "--notes-file", notes_file
        ]
        
        # Add artifacts
        for artifact in artifacts:
            cmd.append(str(artifact))
        
        run_command(cmd, cwd=project_root)
        print(f"✅ GitHub release {version} created")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ GitHub release creation failed: {e}")
        raise
    finally:
        # Clean up temporary file
        Path(notes_file).unlink()


def run_pre_release_checks(project_root: Path) -> None:
    """Run pre-release checks."""
    print("🔍 Running pre-release checks...")
    
    # Run tests
    test_script = project_root / "scripts" / "test.py"
    
    try:
        run_command([
            sys.executable, str(test_script),
            "--lint",
            "--coverage",
            "--parallel"
        ], cwd=project_root)
        
        print("✅ Pre-release checks passed")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Pre-release checks failed: {e}")
        raise


def main():
    """Main release script."""
    parser = argparse.ArgumentParser(description="Release topyaz package")
    parser.add_argument(
        "version",
        help="Version to release (e.g., 1.0.0 or v1.0.0)"
    )
    parser.add_argument(
        "--repository",
        choices=["pypi", "testpypi"],
        default="pypi",
        help="Repository to publish to"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without making changes"
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip pre-release checks"
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip building (assume artifacts exist)"
    )
    parser.add_argument(
        "--skip-publish",
        action="store_true",
        help="Skip publishing to PyPI"
    )
    parser.add_argument(
        "--skip-github",
        action="store_true",
        help="Skip GitHub release creation"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force release even with uncommitted changes"
    )
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent.parent
    print(f"Project root: {project_root}")
    
    # Validate version
    if not validate_version(args.version):
        sys.exit(1)
    
    # Get git info
    git_info = get_git_info(project_root)
    
    # Check for uncommitted changes
    if git_info["has_changes"] and not args.force:
        print("❌ Uncommitted changes detected. Use --force to override.")
        sys.exit(1)
    
    # Check if version is already tagged
    if git_info["current_tag"]:
        print(f"❌ Current commit is already tagged as {git_info['current_tag']}")
        sys.exit(1)
    
    # Run pre-release checks
    if not args.skip_checks:
        run_pre_release_checks(project_root)
    
    # Create git tag
    if not args.dry_run:
        create_git_tag(project_root, args.version)
    
    # Build package
    artifacts = []
    if not args.skip_build:
        artifacts = build_package(project_root)
    
    # Generate release notes
    release_notes = generate_release_notes(
        project_root, 
        args.version, 
        git_info["latest_tag"]
    )
    
    # Publish to PyPI
    if not args.skip_publish:
        publish_to_pypi(project_root, args.repository, args.dry_run)
    
    # Create GitHub release
    if not args.skip_github:
        create_github_release(
            project_root, 
            args.version, 
            release_notes, 
            artifacts, 
            args.dry_run
        )
    
    if args.dry_run:
        print("🧪 Dry run completed successfully!")
    else:
        print(f"🎉 Release {args.version} completed successfully!")
        print(f"📦 Package available at: https://pypi.org/project/topyaz/{args.version.lstrip('v')}/")


if __name__ == "__main__":
    main()