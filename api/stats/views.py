from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils.generics import hardware_info, system_stats


class StatsView(APIView):
    """Stats View

    Returns data for the dashboard widgets. It returns general stats like number of websites, databases,
    storage & RAM stats etc.
    """

    http_method_names = ["get"]
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kw):
        result = system_stats()
        response = Response(result, status=status.HTTP_200_OK)
        return response


class HardwareinfoView(APIView):
    """Hardware Info View

    Returns the information about the server hardware. Only admins are allowed to get these details.
    """

    http_method_names = ["get"]
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kw):
        result = hardware_info()
        response = Response(result, status=status.HTTP_200_OK)
        return response
