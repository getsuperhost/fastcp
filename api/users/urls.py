from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register("", views.UsersViewSet)

app_name = "sshusers"
urlpatterns = [
    path("<int:id>/reset-password/", views.ResetPasswordView().as_view(), name="reset_password"),
    path("", include(router.urls)),
]
