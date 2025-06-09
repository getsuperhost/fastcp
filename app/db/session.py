from sqlalchemy import event, inspect
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
import structlog
from typing import AsyncGenerator
from app.core.config import get_settings


# Create logger
logger = structlog.get_logger(__name__)


# Define settings variable
settings = get_settings()

# If using pgBouncer or no local pooling:
engine = create_async_engine(
    settings.DB_URL, echo=settings.IS_DEBUG, pool_pre_ping=True
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get an async session, ensures cleanup."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


def get_friendly_name(obj):
    return getattr(obj.__class__, '__friendlyname__', None)


@event.listens_for(Session, 'after_flush')
def audit(session, flush_context):
    # We'll loop over created, updated and deleted in one go
    for action, col in (
        ('created', session.new),
        ('updated', session.dirty),
        ('deleted', session.deleted),
    ):
        for obj in col:
            # skip dirty entries that aren’t real UPDATE
            if action == 'updated' and not session.is_modified(
                obj, include_collections=False
            ):
                continue

            tbl = getattr(obj.__class__, '__tablename__', None)
            if not tbl:
                continue

            state = inspect(obj)
            # build a per-attribute diff only for updates
            changes = []
            if action == 'updated':
                for attr in state.attrs:
                    hist = attr.history
                    if not hist.has_changes():
                        continue
                    old = hist.deleted[0] if hist.deleted else None
                    new = hist.added[0] if hist.added else None
                    changes.append({'field': attr.key, 'old': old, 'new': new})

            # derive a dynamic event name: "<table>.<action>"
            event_name = f'{tbl}.{action}'

            # emit with structlog
            logs_payload = {'target_id': str(obj.id), 'changes': changes or None}
            if action == 'deleted':
                logger.warning(event_name, **logs_payload)
            else:
                logger.info(event_name, **logs_payload)