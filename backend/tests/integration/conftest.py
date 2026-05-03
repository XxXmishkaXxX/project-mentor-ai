from unittest.mock import AsyncMock

import pytest
from cashews import cache
from litestar.testing import AsyncTestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app import global_store
from app.global_.settings import Settings
from app.store.pg.config import DatabaseConfig
from app.store.pg.models import Base
from app.store.store import Store
from app.users.db import UserModel


@pytest.fixture(scope="session")
async def store(settings: Settings) -> Store:
    _store = Store(settings)

    db_config = DatabaseConfig.from_settings(settings.config)
    engine = create_async_engine(
        db_config.url,
        echo=False,
        poolclass=NullPool,
    )
    _store.pg.engine = engine
    _store.pg.session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    cache.setup("mem://")

    if hasattr(_store, "embedder"):
        _store.embedder._client = AsyncMock()
    if hasattr(_store, "retriever"):
        _store.retriever._client = AsyncMock()
    if hasattr(_store, "llm"):
        _store.llm._client = AsyncMock()

    yield _store

    await engine.dispose()


@pytest.fixture(autouse=True)
async def _clean_db(store: Store) -> None:
    async with store.pg.session() as session:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(
                text(f"TRUNCATE TABLE {table.name} CASCADE"),
            )
        await session.commit()


def _create_app_for_tests(store: Store, settings: Settings):
    from litestar import Litestar, MediaType, get
    from litestar.openapi import OpenAPIConfig

    from app.auth.views import AuthView
    from app.chat.views import ChatView
    from app.users.views import UserView
    from app.web.errors import (
        after_exception_handler,
        internal_server_error_handler,
    )
    from app.web.middlewares import SessionMiddleware
    from app.web.request import AppRequest

    @get("/api/health", media_type=MediaType.JSON)
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    global_store.set(store)

    return Litestar(
        route_handlers=[
            health_check,
            AuthView,
            UserView,
            ChatView,
        ],
        request_class=AppRequest,
        middleware=[SessionMiddleware],
        after_exception=[after_exception_handler],
        exception_handlers={
            500: internal_server_error_handler,
        },
        debug=settings.debug,
        openapi_config=OpenAPIConfig(
            title="Test API",
            path="/docs",
            version="test",
            root_schema_site="swagger",
        ),
    )


@pytest.fixture(scope="session")
def app(store: Store, settings: Settings):
    return _create_app_for_tests(store, settings)


@pytest.fixture(scope="session")
async def client(app) -> AsyncTestClient:
    async with AsyncTestClient(app=app) as tc:
        yield tc


async def create_user_in_db(
    store: Store,
    *,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "securepass123",
) -> UserModel:
    from app.auth.manager import AuthManager

    password_hash = AuthManager.hash_password(password)
    return await store.user_accessor.create_user(
        username=username,
        email=email,
        password_hash=password_hash,
    )


async def login_user(
    client: AsyncTestClient,
    email: str = "test@example.com",
    password: str = "securepass123",
) -> str:
    resp = await client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 201
    return resp.cookies.get("session_id", "")


@pytest.fixture
async def user(store: Store) -> UserModel:
    return await create_user_in_db(store)


@pytest.fixture
async def authorized_client(
    client: AsyncTestClient,
    user: UserModel,
) -> AsyncTestClient:
    session_id = await login_user(client, user.email)
    client.cookies.set("session_id", session_id)
    yield client
    client.cookies.clear()
