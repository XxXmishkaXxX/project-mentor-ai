from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app import global_settings
from app.global_.settings import path


class Base(DeclarativeBase):
    pass


def get_engine():
    settings = global_settings.get()
    url = path(settings.config, "db", "url")
    if url is None:
        host = path(settings.config, "db", "host", default="localhost")
        port = path(settings.config, "db", "port", default=5432)
        name = path(settings.config, "db", "name", default="mentor_ai")
        user = path(settings.config, "db", "user", default="postgres")
        password = path(settings.config, "db", "password", default="postgres")
        url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"
    return create_async_engine(url, echo=settings.debug)


def get_session_factory(engine=None):
    if engine is None:
        engine = get_engine()
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
