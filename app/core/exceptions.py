from fastapi import HTTPException, status


class InvalidCredentials(HTTPException):
    """
    Raised when the provided Unix username or password are invalid.
    """
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials.'
        )
