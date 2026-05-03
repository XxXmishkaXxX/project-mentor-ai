from __future__ import annotations

from typing import TYPE_CHECKING

import click

from app.global_.settings import path

if TYPE_CHECKING:
    from app.global_.settings import Settings


@click.command(name="api", help="run API server")
@click.option(
    "--host",
    default=None,
    envvar="HOST",
    show_envvar=True,
)
@click.option(
    "--port",
    default=None,
    type=int,
    envvar="PORT",
    show_envvar=True,
)
@click.option(
    "--workers",
    default=1,
    type=int,
    envvar="WORKERS",
    show_envvar=True,
)
@click.pass_obj
def api(
    settings: Settings,
    host: str | None,
    port: int | None,
    workers: int,
) -> None:
    import uvicorn

    config = settings.config
    host = host or path(config, "web", "host", default="0.0.0.0")  # noqa: S104
    port = port or path(config, "web", "port", default=8000)

    uvicorn.run(
        "app.entrypoints.api.app:create_app",
        factory=True,
        host=host,
        port=port,
        workers=workers,
        loop="uvloop" if settings.use_uvloop else "asyncio",
        log_level="debug" if settings.debug else "info",
    )
