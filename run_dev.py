#!/usr/bin/env python
"""Development server runner with debug mode enabled."""
import os
import sys

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    # Enable debug mode for development
    os.environ.setdefault("IS_DEBUG", "1")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fastcp.settings")

    # Run the development server
    sys.argv = ["manage.py", "runserver", "0.0.0.0:8899"]
    execute_from_command_line(sys.argv)
