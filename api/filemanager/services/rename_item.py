import os

from .base_service import BaseService


class RenameItemService(BaseService):
    """Rename item.

    Responsible to rename a file or a directory.
    """

    def __init__(self, request):
        self.request = request

    def rename_item(self, validated_data: dict) -> bool:
        """Rename item.

        Args:
            validated_data (dict): Validated data from serializer.

        Returns:
            bool: True on success and False on failure.
        """
        root_path = validated_data.get("path")
        new_name = validated_data.get("new_name")
        old_name = validated_data.get("old_name")
        user = self.request.user

        if not all([root_path, new_name, old_name]):
            return False

        # Type assertions for mypy
        assert root_path is not None
        assert new_name is not None
        assert old_name is not None

        old_path = os.path.join(root_path, old_name)
        new_path = os.path.join(root_path, new_name)
        if all(
            [
                os.path.exists(old_path),
                not os.path.exists(new_path),
                self.is_allowed(new_path, user),
                self.is_allowed(old_path, user),
            ]
        ):
            try:
                os.rename(old_path, new_path)
                self.fix_ownership(new_path)
                return True
            except Exception:
                pass

        return False
