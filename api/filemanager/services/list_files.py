from pathlib import Path

from django.core.paginator import EmptyPage, Paginator

from core.utils import filesystem as cpfs

from .base_service import BaseService


class ListFileService(BaseService):
    """List Files

    Scans filesystem for path and returns dict with paginated paths list.
    """

    def __init__(self, request):
        self.request = request

    def get_files_list(self, validated_data: dict) -> dict:
        """Gets the list of files

        Gets the paginated list of files and directories paths.

        Args:
            validated_data (dict): The validated data from serializers.

        Returns:
            dict: Containing paginated filesystem paths list.
        """
        path = validated_data.get("path")
        search = validated_data.get("search")
        user = self.request.user

        if path:
            path_obj = Path(path)
            files = []
            for p in path_obj.iterdir():
                try:
                    data = cpfs.get_path_info(p)
                    name = data.get("name", "")
                    if (not search or
                            (name and search.lower() in name.lower())):
                        if self.is_allowed(str(p), user):
                            files.append(data)
                except PermissionError:
                    pass

            paginator = Paginator(files, 30)
            page_num = validated_data.get("page", 1)
            if not page_num:
                page_num = 1
            try:
                page = paginator.page(page_num)
            except EmptyPage:
                page = paginator.page(1)

            try:
                next_page = page.next_page_number()
            except EmptyPage:
                next_page = None

            try:
                previous_page = page.previous_page_number()
            except EmptyPage:
                previous_page = None

            try:
                path_str = str(path_obj)
                segments = enumerate([
                    p for p in path_str.split("/") if len(p.strip()) > 0
                ])
            except Exception:
                segments = []

            data = {
                "segments": segments,
                "links": {"next": next_page, "previous": previous_page},
                "count": len(files),
                "results": page.object_list,
            }

            return data
        return {}
