from fastapi import APIRouter
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth import process_login


# Create router
router = APIRouter()


@router.post(
    '/login',
    name='Login',
    description='This endpoint allows a user to login using the Unix system username and password and returns '
                'a JWT that can be used to make authenticated API calls to protected endpoints.',
    response_model=TokenResponse
)
async def login(request: LoginRequest):
    return await process_login(request.username, request.password)
