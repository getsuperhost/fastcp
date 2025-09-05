#!/usr/bin/env python3
"""
FastCP Development Utilities
A collection of utility functions for development workflow
"""

import argparse
import os
import subprocess
from pathlib import Path


class FastCPDevUtils:
    """Development utilities for FastCP project."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "fastcp_env"

    def run_command(self, command, cwd=None, capture_output=False):
        """Run a shell command."""
        try:
            result = subprocess.run(
                command, shell=True, cwd=cwd or self.project_root, capture_output=capture_output, text=True, check=True
            )
            if capture_output:
                return result.stdout.strip() if result.stdout else ""
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {command}")
            print(f"Error: {e}")
            return False

    def setup_development_environment(self):
        """Set up the development environment."""
        print("Setting up FastCP development environment...")

        # Create virtual environment if it doesn't exist
        if not self.venv_path.exists():
            print("Creating virtual environment...")
            self.run_command("python3 -m venv fastcp_env")

        # Activate virtual environment and install dependencies
        print("Installing Python dependencies...")
        pip_cmd = f"{self.venv_path}/bin/pip"
        self.run_command(f"{pip_cmd} install --upgrade pip")
        self.run_command(f"{pip_cmd} install -r requirements.txt")

        # Install Node.js dependencies
        if (self.project_root / "package.json").exists():
            print("Installing Node.js dependencies...")
            self.run_command("npm install")

        print("Development environment setup complete!")

    def run_quality_checks(self):
        """Run all code quality checks."""
        print("Running code quality checks...")

        checks = [
            ("black", "black --check --diff ."),
            ("isort", "isort --check-only --diff ."),
            ("flake8", "flake8 ."),
            ("bandit", "bandit -r . -f json -o security_report.json"),
            ("safety", "safety check --json > safety_report.json"),
        ]

        for name, command in checks:
            print(f"Running {name}...")
            if not self.run_command(command):
                print(f"{name} check failed!")
                return False

        print("All quality checks passed!")
        return True

    def format_code(self):
        """Format code using black and isort."""
        print("Formatting code...")
        self.run_command("black .")
        self.run_command("isort .")
        print("Code formatting complete!")

    def run_tests(self, verbose=False):
        """Run Django tests."""
        print("Running tests...")
        cmd = "python manage.py test"
        if verbose:
            cmd += " --verbosity=2"
        self.run_command(cmd)

    def create_superuser(self):
        """Create Django superuser."""
        print("Creating Django superuser...")
        self.run_command("python manage.py createsuperuser --noinput")

    def collect_static(self):
        """Collect Django static files."""
        print("Collecting static files...")
        self.run_command("python manage.py collectstatic --noinput")

    def migrate_database(self):
        """Run Django migrations."""
        print("Running database migrations...")
        self.run_command("python manage.py migrate")

    def clean_project(self):
        """Clean up temporary files and caches."""
        print("Cleaning project...")

        patterns = [
            "*.pyc",
            "*.pyo",
            "*.pyd",
            "__pycache__",
            "*.egg-info",
            ".pytest_cache",
            ".coverage",
            "node_modules",
            ".cache",
            "*.log",
        ]

        for pattern in patterns:
            cmd1 = f"find . -name '{pattern}' -type f -delete"
            self.run_command(cmd1)
            cmd2 = f"find . -name '{pattern}' -type d -exec rm -rf {{}} +"
            self.run_command(cmd2)

        print("Project cleanup complete!")

    def show_status(self):
        """Show project status."""
        print("FastCP Project Status")
        print("=" * 50)

        # Check Python version
        python_cmd = "python --version"
        python_version = self.run_command(python_cmd, capture_output=True)
        if isinstance(python_version, str):
            print(f"Python: {python_version}")
        else:
            print("Python: Unable to determine version")

        # Check Django version
        django_cmd = "python -c 'import django; print(django.VERSION)'"
        django_version = self.run_command(django_cmd, capture_output=True)
        if isinstance(django_version, str):
            print(f"Django: {django_version}")

        # Check Node.js version
        node_version = self.run_command("node --version", capture_output=True)
        if isinstance(node_version, str):
            print(f"Node.js: {node_version}")

        # Check if virtual environment is active
        venv_active = "VIRTUAL_ENV" in os.environ
        venv_status = "Active" if venv_active else "Inactive"
        print(f"Virtual Environment: {venv_status}")

        # Check database
        db_exists = (self.project_root / "db.sqlite3").exists()
        print(f"Database: {'Exists' if db_exists else 'Not found'}")

        # Check static files
        static_exists = (self.project_root / "staticfiles").exists()
        static_status = "Collected" if static_exists else "Not collected"
        print(f"Static Files: {static_status}")


def main():
    parser = argparse.ArgumentParser(description="FastCP Development Utilities")
    parser.add_argument(
        "command",
        choices=["setup", "quality", "format", "test", "superuser", "static", "migrate", "clean", "status"],
        help="Command to run",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    utils = FastCPDevUtils()

    commands = {
        "setup": utils.setup_development_environment,
        "quality": utils.run_quality_checks,
        "format": utils.format_code,
        "test": lambda: utils.run_tests(args.verbose),
        "superuser": utils.create_superuser,
        "static": utils.collect_static,
        "migrate": utils.migrate_database,
        "clean": utils.clean_project,
        "status": utils.show_status,
    }

    commands[args.command]()


if __name__ == "__main__":
    main()
