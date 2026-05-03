from __future__ import annotations

from litestar import Litestar, MediaType, get
from litestar.openapi import OpenAPIConfig

from app import global_settings


def register_urls() -> list:
    return []


@get("/api/health", media_type=MediaType.JSON)
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


def create_app() -> Litestar:
    settings = global_settings.get()

    return Litestar(
        route_handlers=[
            health_check,
            *register_urls(),
        ],
        debug=settings.debug,
        openapi_config=OpenAPIConfig(
            title="Project Mentor AI API",
            path="/docs",
            version="1.0.0",
            root_schema_site="swagger",
        ),
    )
