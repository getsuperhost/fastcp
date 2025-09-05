import os
import shutil

from .base_service import BaseService


class DeleteItemsService(BaseService):
    """Deletes items.

    Permanently deletes files and directories from disk.
    """

    def __init__(self, request):
        self.request = request

    def delete_items(self, validated_data):
        """Delete items.

        Takes validated serializer data and deletes qualified paths.

        Args:
            validated_data: The serializer validated data.

        Returns:
            bool: True on success and False on failure.
        """
        try:
            paths = validated_data.get("paths").split(",")
            user = self.request.user
            if len(paths):
                for path in paths:
                    if self.is_allowed(path, user):
                        if os.path.isdir(path):
                            try:
                                shutil.rmtree(path)
                            except OSError:
                                pass
                        if os.path.isfile(path):
                            os.remove(path)

                return True
        except Exception:
            pass
