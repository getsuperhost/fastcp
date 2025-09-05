from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

from .utils.auth import do_login

User = get_user_model()


class FastcpAuthBackend(BaseBackend):
    """Custom authentication backend for FastCP with SSH password validation."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """Authenticate user using SSH password validation."""
        if username is None or password is None:
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        # Use our custom authentication function
        if do_login(username, password):
            return user

        return None

    def get_user(self, user_id):
        """Get user by ID."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
