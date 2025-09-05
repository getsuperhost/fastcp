from pathlib import Path

from django.conf import settings


class PhpVersionListService(object):
    """List PHP versions.

    This class scans the PHP installation directory and gets the list of supported PHP versions on the system.
    """

    def get_php_versions(self) -> list:
        path = Path(settings.PHP_INSTALL_PATH)
        versions = []

        # Check if the PHP installation path exists
        if not path.exists():
            # Return default PHP versions if path doesn't exist (e.g., in Docker)
            return ["8.2", "8.1", "8.0", "7.4", "7.3"]

        try:
            for version in path.iterdir():
                if version.is_dir():
                    versions.append(version.name)
            versions.sort(reverse=True)
        except (OSError, PermissionError):
            # If we can't read the directory, return default versions
            return ["8.2", "8.1", "8.0", "7.4", "7.3"]

        return versions
