from litestar import Litestar, MediaType, Response, get
from litestar.config.cors import CORSConfig
from litestar.openapi import OpenAPIConfig
from sqlalchemy import text

from app import global_settings, global_store
from app.auth.views import AuthView
from app.chat.views import ChatView
from app.global_.settings import path
from app.store.store import Store
from app.users.views import UserView
from app.web.errors import (
    after_exception_handler,
    internal_server_error_handler,
)
from app.web.middlewares import SessionMiddleware
from app.web.request import AppRequest


@get("/api/health")
async def health_check() -> Response[dict[str, str]]:
    store = global_store.get()
    statuses: dict[str, str] = {}

    try:
        async with store.pg.session() as session:
            await session.execute(text("SELECT 1"))
        statuses["pg"] = "ok"
    except Exception:  # noqa: BLE001
        statuses["pg"] = "error"

    try:
        await store.cache.client.get("_health_check")
        statuses["redis"] = "ok"
    except Exception:  # noqa: BLE001
        statuses["redis"] = "error"

    if store.is_rag_available:
        try:
            await store.retriever.client.get_collections()
            statuses["qdrant"] = "ok"
        except Exception:  # noqa: BLE001
            statuses["qdrant"] = "error"

    all_ok = all(v == "ok" for v in statuses.values())
    return Response(
        content=statuses,
        status_code=200 if all_ok else 503,
        media_type=MediaType.JSON,
    )


def create_app() -> Litestar:
    settings = global_settings.get()

    store = Store(settings)
    global_store.set(store)

    default_origin = "http://localhost:5173"
    cors_origins_raw: str = path(
        settings.config,
        "cors",
        "origins",
        default=default_origin,
    )
    cors_origins = [o.strip() for o in cors_origins_raw.split(",") if o.strip()]
    if not cors_origins:
        cors_origins = [default_origin]

    async def on_startup() -> None:
        await store.connect_all()

    async def on_shutdown() -> None:
        await store.disconnect_all()

    return Litestar(
        route_handlers=[
            health_check,
            AuthView,
            UserView,
            ChatView,
        ],
        request_class=AppRequest,
        middleware=[SessionMiddleware],
        cors_config=CORSConfig(
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        on_startup=[on_startup],
        on_shutdown=[on_shutdown],
        after_exception=[after_exception_handler],
        exception_handlers={
            500: internal_server_error_handler,
        },
        debug=settings.debug,
        openapi_config=OpenAPIConfig(
            title="Project Mentor AI API",
            path="/docs",
            version="1.0.0",
            root_schema_site="swagger",
        ),
    )
