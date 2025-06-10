from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str = Field(title='Access Token', description='JWT access token.')


class LoginRequest(BaseModel):
    username: str = Field(
        title='Username', description='Unix system username.', example='root'
    )
    password: str = Field(title='Password', description='Unix system password.')
