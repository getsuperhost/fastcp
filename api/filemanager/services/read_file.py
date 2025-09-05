import os

from core.utils import filesystem as cpfs

from .base_service import BaseService


class ReadFileService(BaseService):
    """Read a file.

    Attempts to read file contents from disk and returns the content.
    """

    def __init__(self, request):
        self.request = request

    def read_file(self, validated_data: dict) -> str | None:
        """Read file.

        Reads the file for the provided path and returns the content.

        Args:
            validated_data (dict): Validated data from serializer.

        Returns:
            Content string on success and None on failure.
        """

        user = self.request.user
        path = validated_data.get("path")
        content = None

        if path and self.is_allowed(path, user) and os.path.exists(path):
            PATH_INFO = cpfs.get_path_info(path)

            # Check for file existence, as well as discard
            # files larger than 10MB.

            file_size = PATH_INFO.get("size")
            if file_size is not None and file_size <= 10000000:
                try:
                    with open(path, "rb") as f:
                        raw_content = f.read()
                    content = raw_content.decode("utf-8")
                except UnicodeDecodeError:
                    content = None

        return content
