import os

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import connection
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import redirect, render

from .forms import LoginForm
from .models import User


def health_check(request):
    """Health check endpoint for monitoring and load balancers."""
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    # Check if static files are accessible
    static_root = settings.STATIC_ROOT
    static_status = "healthy" if os.path.exists(static_root) else "unhealthy"

    # Determine overall status
    overall_status = "healthy"
    if db_status != "healthy" or static_status != "healthy":
        overall_status = "unhealthy"

    response_data = {
        "status": overall_status,
        "database": db_status,
        "static_files": static_status,
        "version": getattr(settings, "VERSION", "1.0.0"),
    }

    status_code = 200 if response_data["status"] == "healthy" else 503
    return JsonResponse(response_data, status=status_code)


@user_passes_test(lambda user: not user.is_authenticated, login_url="/", redirect_field_name="")
def sign_in(request):
    """Custom login.

    We are going to validate the SSH login info of the user and then we will
    authenticate their session.
    """
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            user = User.objects.filter(username=username).first()
            login(request, user)
            return redirect("/dashboard")
    context = {"form": form}
    return render(request, "registration/login.html", context=context)


def sign_out(request):
    logout(request)
    return redirect("/dashboard")


@login_required
def download_file(request):
    path = request.GET.get("path")
    user = request.user
    if user.is_superuser:
        BASE_PATH = settings.FILE_MANAGER_ROOT
    else:
        BASE_PATH = os.path.join(settings.FILE_MANAGER_ROOT, user.username)

    if path and path.startswith(BASE_PATH) and os.path.exists(path):
        response = FileResponse(open(path, "rb"))
        return response
    raise Http404
