from datetime import datetime
from zoneinfo import ZoneInfo
from app.core.config import get_settings


# Settings
settings = get_settings()

TIMEZONE = ZoneInfo(settings.TIMEZONE)


def now() -> datetime:
    return datetime.now(tz=TIMEZONE)
