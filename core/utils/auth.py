import crypt
import spwd

from django.conf import settings


def do_login(user, password):
    """Tries to authenticate an SSH user.

    We are validating SSH login details to authenticate the sessions.

    Args:
        user (str): The SSH user's username.
        password (str): The SSH user's plain text password.

    Returns:
        bool: Returns True on success and False on failure.
    """
    # In DEBUG mode, bypass SSH authentication for development
    if settings.DEBUG:
        # Simple development authentication
        # For admin user, accept any password
        if user == "admin":
            return True
        # For other users, accept password matching username
        return user == password

    try:
        enc_pwd = spwd.getspnam(user)[1]
        if enc_pwd in ["NP", "!", "", None]:
            # User does not have a password
            pass
        if enc_pwd in ["LK", "*"]:
            # Account is locked
            pass
        if enc_pwd == "!!":
            # Password has expired
            pass
        if crypt.crypt(password, enc_pwd) == enc_pwd:
            return True
    except KeyError:
        return False
    return False
