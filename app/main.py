from fastapi import FastAPI
from app.core.config import get_settings
from app.routes.auth import router as auth_router

# Settings
settings = get_settings()


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)


# Include routers
app.include_router(auth_router, prefix='/auth', tags=['Authentication'])
