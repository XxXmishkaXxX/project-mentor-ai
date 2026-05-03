from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import Any, TypeVar

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.base.accessor import BaseAccessor
from app.store.pg.config import DatabaseConfig

T = TypeVar("T")

_active_session: ContextVar[AsyncSession | None] = ContextVar(
    "_active_session",
    default=None,
)


class PgAccessor(BaseAccessor):
    engine: AsyncEngine | None = None
    session_factory: async_sessionmaker[AsyncSession] | None = None

    async def connect(self) -> None:
        config = DatabaseConfig.from_settings(
            self.store.settings.config,
        )
        self.engine = create_async_engine(
            config.url,
            echo=self.store.settings.debug,
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def disconnect(self) -> None:
        if self.engine:
            await self.engine.dispose()

    def session(self) -> AsyncSession:
        if self.session_factory is None:
            msg = "PgAccessor is not connected"
            raise RuntimeError(msg)
        return self.session_factory()

    @property
    def in_transaction(self) -> bool:
        return _active_session.get(None) is not None

    @asynccontextmanager
    async def _get_session(self):
        """Yield the active transaction session or create a standalone one."""
        active = _active_session.get(None)
        if active is not None:
            yield active
            return
        async with self.session() as session:
            yield session

    @asynccontextmanager
    async def begin(self):
        """Shared transaction scope.

        All PgAccessor operations within this context share a single
        session. Commits on success, rolls back on any exception.
        Supports nesting — inner ``begin()`` calls reuse the outer session.
        """
        active = _active_session.get(None)
        if active is not None:
            yield active
            return

        async with self.session() as session:
            token = _active_session.set(session)
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                _active_session.reset(token)

    async def execute(self, stmt: Any) -> Any:
        async with self._get_session() as session:
            result = await session.execute(stmt)
            if not self.in_transaction:
                await session.commit()
            return result

    async def scalar_one_or_none(self, stmt: Any) -> Any:
        async with self._get_session() as session:
            result = await session.execute(stmt)
            if not self.in_transaction:
                await session.commit()
            return result.scalar_one_or_none()

    async def scalar_one(self, stmt: Any) -> Any:
        async with self._get_session() as session:
            result = await session.execute(stmt)
            if not self.in_transaction:
                await session.commit()
            return result.scalar_one()

    async def scalars_all(self, stmt: Any) -> list[Any]:
        async with self._get_session() as session:
            result = await session.execute(stmt)
            if not self.in_transaction:
                await session.commit()
            return list(result.scalars().all())

    async def add_one(self, instance: T) -> T:
        async with self._get_session() as session:
            session.add(instance)
            if self.in_transaction:
                await session.flush()
            else:
                await session.commit()
            await session.refresh(instance)
            return instance
