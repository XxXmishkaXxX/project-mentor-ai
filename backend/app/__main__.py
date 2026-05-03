import logging

import click

from app import global_settings
from app.global_.autodiscover import autodiscover_commands
from app.global_.log import LogJson, setup_logging
from app.global_.settings import (
    EnvLoader,
    FileLoader,
    OneOfLoader,
    Settings,
)


@click.group()
@click.option(
    "--config",
    help="config file path",
    default=None,
    envvar="CONFIG",
    show_envvar=True,
)
@click.option(
    "--log-json",
    help="turn on json logging",
    type=click.Choice(list(LogJson.__members__.keys())),
    default="off",
    envvar="LOG_JSON",
    show_envvar=True,
)
@click.option(
    "--debug",
    help="turn on the debug",
    default=None,
    is_flag=True,
    envvar="DEBUG",
    show_envvar=True,
)
@click.option(
    "--uvloop",
    help="enable uvloop (default: on)",
    default=True,
    type=bool,
    is_flag=False,
    envvar="UVLOOP_ENABLED",
    show_envvar=True,
)
@click.pass_context
def cli(
    ctx: click.Context,
    config: str | None,
    debug: bool | None,
    log_json: str,
    uvloop: bool,
) -> None:
    file_loaders: list[FileLoader] = []
    if config is not None:
        file_loaders.append(FileLoader(config))
    file_loaders.append(FileLoader("local/etc/config.yaml"))

    ctx.obj = Settings(
        loaders=[
            FileLoader("etc/config.yaml"),
            OneOfLoader(file_loaders),
            EnvLoader(),
        ],
        debug=debug,
        use_uvloop=uvloop,
    )
    ctx.obj.load_config()
    global_settings.set(ctx.obj)

    setup_logging(
        log_json=LogJson(log_json),
        alter_loggers_levels={
            "urllib3": logging.INFO,
            "httpx": logging.INFO,
            "httpcore": logging.INFO,
            "redis": logging.WARNING,
            "cashews": logging.WARNING,
        },
    )


autodiscover_commands(cli, "app.entrypoints")


@cli.command(
    help="run alembic migrations",
    context_settings={"ignore_unknown_options": True},
)
@click.argument("args", nargs=-1)
@click.pass_obj
def migrate(_settings: Settings, args: tuple[str, ...]) -> None:
    import inspect
    import os

    import alembic.config

    from app.store import pg

    pg_path = os.path.dirname(inspect.getfile(pg))
    alembic_ini = os.path.join(pg_path, "alembic.ini")
    alembic.config.main(
        ["-c", alembic_ini, *args],
        prog="python -m app migrate",
    )


if __name__ == "__main__":
    cli()
