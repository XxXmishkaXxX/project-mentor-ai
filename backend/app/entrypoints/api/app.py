from litestar import Litestar, MediaType, get
from litestar.openapi import OpenAPIConfig

from app import global_settings, global_store
from app.auth.views import AuthView
from app.chat.views import ChatView
from app.store.store import Store
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


def create_app() -> Litestar:
    settings = global_settings.get()

    store = Store(settings)
    global_store.set(store)

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
