import structlog
from litestar import Controller

from app import global_store
from app.store.store import Store


class BaseView(Controller):
    @property
    def store(self) -> Store:
        return global_store.get()

    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        return structlog.get_logger(type(self).__name__)
