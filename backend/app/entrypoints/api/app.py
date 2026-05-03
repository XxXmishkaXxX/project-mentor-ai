from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.openapi import OpenAPIConfig

from app import global_settings
from app.auth.views import AuthView
from app.chat.views import ChatView
from app.entrypoints.api.health import health_check
from app.global_.settings import path
from app.users.views import UserView
from app.web.middlewares import SessionMiddleware
from app.web.plugin import StorePlugin
from app.web.request import Request


def create_app() -> Litestar:
    settings = global_settings.get()
    plugin = StorePlugin(settings)

    return Litestar(
        route_handlers=[
            health_check,
            AuthView,
            UserView,
            ChatView,
        ],
        plugins=[plugin],
        request_class=Request,
        middleware=[SessionMiddleware],
        cors_config=CORSConfig(
            allow_origins=[
                *path(
                    settings.config,
                    "security",
                    "cors_allowed_domains",
                    default=[],
                ),
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        debug=settings.debug,
        openapi_config=OpenAPIConfig(
            title="Project Mentor AI API",
            path="/docs",
            version="1.0.0",
            root_schema_site="swagger",
        ),
    )
