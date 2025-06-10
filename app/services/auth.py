from datetime import timedelta
import jwt
from app.core.timezone import now
from app.core.config import get_settings
from app.services.pam import PamAuthenticator
from app.core.exceptions import InvalidCredentials


# Create settings object
settings = get_settings()


def create_jwt(username, hours_valid=1):
    utc_now = now()
    payload = {
        'sub': username,
        'iat': utc_now,
        'exp': utc_now + timedelta(hours=hours_valid),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


def verify_jwt(token):
    try:
        decoded = jwt.decode(
            token, settings.JWT_SECRET, algorithms=settings.JWT_ALGORITHM
        )
        return decoded  # Returns the payload if valid
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None


async def process_login(username: str, password: str) -> dict:
    pam = PamAuthenticator()

    # Validate Unix username and password
    if not pam.authenticate(username, password):
        raise InvalidCredentials()

    # Generate and return a signed JWT
    return {'access_token': create_jwt(username)}
