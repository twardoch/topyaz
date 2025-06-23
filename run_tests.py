# /// script
# dependencies = ["pytest", "pytest-cov", "uv"]
# ///
# this_file: run_tests.py
import subprocess
import sys
import os

def main():
    project_root = os.getcwd()
    print(f"Installing current package from {project_root} with [test] extras using uv pip...")

    install_command = [
        "uv", "pip", "install", "-e", f"{project_root}[test]"
    ]

    try:
        install_process = subprocess.run(install_command, check=True, capture_output=True, text=True)
        print("Package installed successfully.")
        if install_process.stdout: print("Install stdout:\n", install_process.stdout)
        if install_process.stderr: print("Install stderr:\n", install_process.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install package using 'uv pip install -e .[test]': {e}")
        if e.stdout: print("stdout:\n", e.stdout)
        if e.stderr: print("stderr:\n", e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Failed to run 'uv pip install': 'uv' command not found. Ensure uv is in PATH or script dependencies.")
        sys.exit(1)

    print("Attempting to run tests with pytest...")
    command = [
        sys.executable, "-m", "pytest",
        "--cov-report=term-missing",
        "--cov-config=pyproject.toml",
        "--cov=src/topyaz",
        "--cov=tests",
        "-v",
        "tests/"
    ]

    print(f"Running command: {' '.join(command)}")
    try:
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        print("Pytest ran successfully (all tests passed).")
        if process.stdout: print("stdout:\n", process.stdout)
        if process.stderr: print("stderr:\n", process.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Pytest execution finished with non-zero exit code ({e.returncode}). See output below.")
        if e.stdout: print("stdout:\n", e.stdout)
        if e.stderr: print("stderr:\n", e.stderr)
        sys.exit(e.returncode)
    except FileNotFoundError:
        print(f"Failed to run pytest: The 'pytest' module or Python itself not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during test execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
