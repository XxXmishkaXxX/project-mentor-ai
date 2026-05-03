import asyncio
from typing import Any, ClassVar

import click
import structlog

from app import global_store
from app.global_.settings import Settings
from app.store.store import Store


class BaseCommand:
    """
    Base class for CLI commands with managed Store lifecycle.

    Subclasses must define:
        name: str — click command name
        help: str — click help text

    And implement:
        async def execute(self, **kwargs) -> None

    Optionally override:
        click_options() — list of click.option decorators
    """

    name: ClassVar[str]
    help: ClassVar[str] = ""
    command: ClassVar[click.Command]

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if not getattr(cls, "name", None):
            return
        cls.command = cls._build_click_command()

    def __init__(self, store: Store) -> None:
        self.store = store
        self.logger = structlog.get_logger(self.name)

    @classmethod
    def click_options(cls) -> list:
        return []

    async def execute(self, **kwargs: Any) -> None:
        raise NotImplementedError

    @classmethod
    def _build_click_command(cls) -> click.Command:
        async def _run(settings: Settings, **kwargs: Any) -> None:
            store = Store(settings)
            global_store.set(store)
            cmd = cls(store)
            try:
                await store.connect_all()
                await cmd.execute(**kwargs)
            finally:
                await store.disconnect_all()

        @click.pass_obj
        def callback(settings: Settings, **kwargs: Any) -> None:
            asyncio.run(_run(settings, **kwargs))

        for option in reversed(cls.click_options()):
            callback = option(callback)

        return click.command(name=cls.name, help=cls.help)(callback)
