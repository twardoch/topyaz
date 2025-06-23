# /// script
# dependencies = ["build", "hatchling", "hatch-vcs"]
# ///
# this_file: run_build.py
import subprocess
import sys

def main():
    print("Attempting to build the project using 'python -m build'...")
    # Standard arguments for python -m build.
    # It will pick up backend and hooks from pyproject.toml.
    command = [sys.executable, "-m", "build", "--wheel", "--sdist"]

    print(f"Running command: {' '.join(command)}")
    try:
        # Using check=True to raise an error if build fails
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        print("'python -m build' ran successfully.")
        if process.stdout: # Build tool usually logs to stderr
            print("stdout:\n", process.stdout)
        if process.stderr:
            print("stderr:\n", process.stderr)
        print("\nBuild artifacts should be in the 'dist/' directory.")

    except subprocess.CalledProcessError as e:
        print(f"'python -m build' execution failed with CalledProcessError (code {e.returncode}):")
        if e.stdout: print("stdout:\n", e.stdout) # stdout might contain useful info too
        if e.stderr: print("stderr:\n", e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        # This case should ideally not happen if dependencies are correctly installed by uv run -s
        print(f"Failed to run 'python -m build': The 'build' module or Python itself not found in expected path.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during build: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
