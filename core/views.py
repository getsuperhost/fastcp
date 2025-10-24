import os

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render

from .forms import LoginForm


@user_passes_test(lambda user: not user.is_authenticated, login_url='/', redirect_field_name=None)
def sign_in(request):
    """Custom login.

    For development, we use Django's authentication system.
    """
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            return redirect('/dashboard')
    context = {
        'form': form
    }
    return render(request, 'registration/login.html', context=context)

def sign_out(request):
    logout(request)
    return redirect('/dashboard')

@login_required
def download_file(request):
    path = request.GET.get('path')
    user = request.user
    if user.is_superuser:
        base_path = settings.FILE_MANAGER_ROOT
    else:
        base_path = os.path.join(settings.FILE_MANAGER_ROOT, user.username)

    # Normalize base path to ensure it ends with separator
    base_path = os.path.abspath(base_path)
    if not base_path.endswith(os.sep):
        base_path += os.sep

    if path:
        # Clean and validate the requested path
        # Remove any leading slashes and dangerous sequences
        path = path.lstrip('/').replace('..', '').replace('//', '/')

        # Build full path and resolve any symlinks
        full_path = os.path.abspath(os.path.join(base_path, path))

        # Ensure the resolved path is within the base directory
        if (full_path.startswith(base_path) and
            os.path.exists(full_path) and
            os.path.isfile(full_path) and
            os.path.commonpath([full_path, base_path]) == base_path):

            try:
                with open(full_path, 'rb') as f:
                    response = FileResponse(f)
                    return response
            except (IOError, OSError):
                pass

    raise Http404
