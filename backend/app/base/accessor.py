from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from app.store.store import Store


class BaseAccessor:
    def __init__(self, store: "Store") -> None:
        self.store = store
        self.logger = structlog.get_logger(type(self).__name__)

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass
