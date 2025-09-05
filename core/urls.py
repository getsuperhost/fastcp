from django.urls import path

from . import views

app_name = "sites"
urlpatterns = [
    path("health/", views.health_check, name="health_check"),
    path("sign-in/", views.sign_in, name="login"),
    path("sign-out/", views.sign_out, name="logout"),
    path("download-file/", views.download_file, name="download"),
]
