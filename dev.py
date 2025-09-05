#!/usr/bin/env python
"""FastCP Development Setup and Management Script."""
import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(command, cwd=None, check=True, env=None):
    """Run a shell command."""
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, env=env)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result


def setup_environment():
    """Set up the development environment."""
    print("Setting up FastCP development environment...")

    # Check if virtual environment exists
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        run_command([sys.executable, "-m", "venv", ".venv"])

    # Activate virtual environment and install dependencies
    print("Installing dependencies...")
    pip_cmd = [str(venv_path / "bin" / "pip"), "install", "-r", "requirements.txt"]
    run_command(pip_cmd)

    # Run migrations
    print("Running database migrations...")
    python_cmd = [str(venv_path / "bin" / "python"), "manage.py", "migrate"]
    env = os.environ.copy()
    env.update({"DJANGO_SETTINGS_MODULE": "fastcp.settings", "IS_DEBUG": "1"})
    run_command(python_cmd, env=env)

    # Collect static files
    print("Collecting static files...")
    python_cmd = [str(venv_path / "bin" / "python"), "manage.py", "collectstatic", "--noinput"]
    run_command(python_cmd, env=env)

    print("Development environment setup complete!")


def run_server(port=8899):
    """Run the development server."""
    print(f"Starting development server on port {port}...")
    venv_path = Path(".venv")
    python_cmd = [str(venv_path / "bin" / "python"), "manage.py", "runserver", f"0.0.0.0:{port}"]
    env = os.environ.copy()
    env.update({"DJANGO_SETTINGS_MODULE": "fastcp.settings", "IS_DEBUG": "1"})
    run_command(python_cmd, env=env, check=False)


def run_tests():
    """Run the test suite."""
    print("Running tests...")
    venv_path = Path(".venv")
    python_cmd = [str(venv_path / "bin" / "python"), "-m", "pytest", "tests.py", "test_extended.py", "--verbosity=2"]
    env = os.environ.copy()
    env.update({"DJANGO_SETTINGS_MODULE": "fastcp.settings", "IS_DEBUG": "1"})
    run_command(python_cmd, env=env, check=False)


def run_linting():
    """Run code linting."""
    print("Running code linting...")
    venv_path = Path(".venv")
    python_cmd = [
        str(venv_path / "bin" / "python"),
        "-m",
        "flake8",
        ".",
        "--count",
        "--select=E9,F63,F7,F82",
        "--show-source",
        "--statistics",
    ]
    run_command(python_cmd, check=False)


def create_superuser():
    """Create a Django superuser."""
    print("Creating superuser...")
    venv_path = Path(".venv")
    python_cmd = [str(venv_path / "bin" / "python"), "manage.py", "createsuperuser"]
    env = os.environ.copy()
    env.update({"DJANGO_SETTINGS_MODULE": "fastcp.settings", "IS_DEBUG": "1"})
    run_command(python_cmd, env=env, check=False)


def main():
    parser = argparse.ArgumentParser(description="FastCP Development Management Script")
    parser.add_argument("command", choices=["setup", "server", "test", "lint", "superuser"], help="Command to run")
    parser.add_argument("--port", type=int, default=8899, help="Port for development server")

    args = parser.parse_args()

    if args.command == "setup":
        setup_environment()
    elif args.command == "server":
        run_server(args.port)
    elif args.command == "test":
        run_tests()
    elif args.command == "lint":
        run_linting()
    elif args.command == "superuser":
        create_superuser()


if __name__ == "__main__":
    main()
