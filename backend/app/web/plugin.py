from litestar.config.app import AppConfig
from litestar.plugins import InitPluginProtocol
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR

from app import global_store
from app.global_.settings import Settings
from app.store.store import Store
from app.web.errors import (
    after_exception_handler,
    internal_server_error_handler,
)


class StorePlugin(InitPluginProtocol):
    """Litestar lifecycle plugin that manages the Store.

    Creates the :class:`Store`, registers it in ``global_store``
    and hooks ``connect_all`` / ``disconnect_all`` into the
    application startup / shutdown cycle.  Also registers the
    global exception handlers.
    """

    def __init__(self, settings: Settings) -> None:
        self._store = Store(settings)
        global_store.set(self._store)

    @property
    def store(self) -> Store:
        return self._store

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        app_config.on_startup.append(self._store.connect_all)
        app_config.on_shutdown.append(self._store.disconnect_all)

        app_config.after_exception.append(after_exception_handler)
        app_config.exception_handlers[HTTP_500_INTERNAL_SERVER_ERROR] = (
            internal_server_error_handler
        )

        return app_config
