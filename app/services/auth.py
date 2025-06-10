from app.services.pam import PamAuthenticator
from app.core.exceptions import InvalidCredentials


def create_jwt(username, secret, hours_valid=1):
    payload = {
        'sub': username,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=hours_valid)
    }
    token = jwt.encode(payload, secret, algorithm='HS256')
    return token


def verify_jwt(token, secret):
    try:
        decoded = jwt.decode(token, secret, algorithms=['HS256'])
        return decoded  # Returns the payload if valid
    except jwt.ExpiredSignatureError:
        return None     # Token has expired
    except jwt.InvalidTokenError:
        return None


async def process_login(username: str, password: str) -> dict:
    pam = PamAuthenticator()

    # Validate Unix username and password
    if not pam.authenticate(username, password):
        raise InvalidCredentials()

    # Generate and return a signed JWT
    return {
        'access_token': 'test'
    }
