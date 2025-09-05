import os
import shutil

from .base_service import BaseService


class MoveDataService(BaseService):
    """Move data.

    Responsible to move or copy items from one location to another.
    """

    def __init__(self, request):
        self.request = request

    def move_data(self, validated_data: dict) -> bool:
        """Move data.

        Args:
            validated_data (dict): Validated data from serializer.

        Returns:
            bool: True on success and False on failure.
        """
        dest_root = validated_data.get("path")
        user = self.request.user

        errors = False
        if dest_root and self.is_allowed(dest_root, user):
            paths_str = validated_data.get("paths")
            if paths_str:
                paths = paths_str.split(",")
                if len(paths):
                    for p in paths:
                        try:
                            if validated_data.get("action") == "move":
                                shutil.move(p, dest_root)
                            else:
                                if os.path.isdir(p):
                                    dest = os.path.join(
                                        dest_root, os.path.basename(p)
                                    )
                                    shutil.copytree(p, dest)
                                else:
                                    shutil.copy2(p, dest_root)
                        except Exception:
                            errors = True

            self.fix_ownership(dest_root)

        if errors:
            return False
        else:
            return True
