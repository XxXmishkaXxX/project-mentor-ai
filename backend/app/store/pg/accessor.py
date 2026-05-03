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

    async def execute(self, stmt: Any) -> Any:
        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()
            return result

    async def scalar_one_or_none(self, stmt: Any) -> Any:
        async with self.session() as session:
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def scalar_one(self, stmt: Any) -> Any:
        async with self.session() as session:
            result = await session.execute(stmt)
            return result.scalar_one()

    async def scalars_all(self, stmt: Any) -> list[Any]:
        async with self.session() as session:
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def add_one(self, instance: T) -> T:
        async with self.session() as session:
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance
