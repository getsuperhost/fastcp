from django.conf import settings
import os
import shutil
from .base_service import BaseService


class DeleteItemsService(BaseService):
    """Deletes items.
    
    Deletes the provided paths. This permanently deletes both files and directories from the disk.
    """
    
    def __init__(self, request):
        self.request = request
    
    def delete_items(self, validated_data):
        """Delete items.
        
        This method takes the validated serializer data from a view and it deletes the qualified paths.
        
        Args:
            validated_data: The serializer validated data.
        
        Returns:
            bool: True on success and False on failure.
        """
        try:
            paths = validated_data.get('paths').split(',')
            user = self.request.user
            if len(paths):
                for path in paths:
                    if self.is_allowed(path, user):
                        if os.path.isdir(path):
                            try:
                                shutil.rmtree(path)
                            except (OSError, IOError, PermissionError):
                                return False
                        if os.path.isfile(path):
                            os.remove(path)
                
                return True
        except (ValueError, AttributeError):
            return False