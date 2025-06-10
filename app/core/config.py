from pathlib import Path
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# We define model config, so we will only load values from env variables with prefix FASTCP_ as well as
# we ignore the env variable letter cases when reading them.
model_config = SettingsConfigDict(
    env_prefix='FASTCP_',
    case_sensitive=False
)


class AppSettings(BaseSettings):
    """
    The global settings for the application. We are using Pydantic settings to manage our application settings,
    and it reads environment variables to override the default values that we define here.
    """
    model_config = model_config

    IS_DEBUG: bool = Field(
        title='Debug Mode',
        description='Designates either the application is in debug mode or not.',
        default=False
    )
    APP_NAME: str = Field(
        title='App Name',
        description='Name of the application.',
        default='FastCP'
    )
    APP_DESCRIPTION: str = Field(
        title='App Description',
        description='The description of the app.',
        default='FastCP is a modern, minimal control panel to manage Ubuntu servers to run web applications.'
    )
    APP_VERSION: str = Field(
        title='Application Version',
        description='The current version of the application.',
        default='2.0.0'
    )
    TIMEZONE: str = Field(default='UTC')
    ROOT_DIR: Path = Path(__file__).parent.parent.parent

    # DB Settings
    DB_URL: str = Field(
        title='Database URL',
        description='The DSN of the database.',
        default=f'sqlite+aiosqlite:///{ROOT_DIR}/static/db.sqlite3'
    )


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
