from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app import global_settings
from app.store.pg.config import DatabaseConfig
from app.store.pg.models import Base as Base


def get_engine():
    """Used by Alembic migrations only — runtime uses PgAccessor."""
    settings = global_settings.get()
    config = DatabaseConfig.from_settings(settings.config)
    return create_async_engine(config.url, echo=settings.debug)


def get_session_factory(engine=None):
    if engine is None:
        engine = get_engine()
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
