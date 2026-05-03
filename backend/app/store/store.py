from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from app.base.accessor import BaseAccessor
    from app.global_.settings import Settings


class Store:
    __frozen__ = False

    def __init__(self, settings: "Settings") -> None:
        self._logger = structlog.get_logger("store")
        self._settings = settings
        self._accessors: dict[str, "BaseAccessor"] = {}
        self.__freeze__()

        from app.auth.accessor import SessionAccessor
        from app.auth.manager import AuthManager
        from app.rag.config import is_rag_configured
        from app.store.cache import CacheAccessor
        from app.store.pg.accessor import PgAccessor
        from app.users.accessor import UserAccessor
        from app.users.manager import UserManager

        self.pg = PgAccessor(self)
        self.cache = CacheAccessor(self)

        self.user_accessor = UserAccessor(self)
        self.session_accessor = SessionAccessor(self)

        self._rag_available = is_rag_configured(settings.config)
        if self._rag_available:
            from app.rag.accessors import (
                EmbedderAccessor,
                LLMAccessor,
                RetrieverAccessor,
            )
            from app.rag.manager import RAGManager

            self.embedder = EmbedderAccessor(self)
            self.retriever = RetrieverAccessor(self)
            self.llm = LLMAccessor(self)
            self.rag_manager = RAGManager(self)
        else:
            self._logger.warning(
                "RAG not configured — qwen.api_base_url is empty, "
                "skipping RAG accessors",
            )

        from app.chat.accessor import ChatAccessor
        from app.chat.manager import ChatManager

        self.chat_accessor = ChatAccessor(self)

        self.user_manager = UserManager(self)
        self.auth_manager = AuthManager(self)
        self.chat_manager = ChatManager(self)

    @property
    def is_rag_available(self) -> bool:
        return self._rag_available

    @property
    def settings(self) -> "Settings":
        return self._settings

    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        return self._logger

    def __freeze__(self) -> None:
        self.__frozen__ = True

    def __getattribute__(self, name: str):
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            if name in self._accessors:
                return self._accessors[name]
            raise AttributeError(
                f"Accessor '{name}' not found",
            ) from e

    def __setattr__(self, key: str, value) -> None:
        from app.base.accessor import BaseAccessor

        if (
            self.__frozen__
            and not hasattr(self, key)
            and isinstance(value, BaseAccessor)
        ):
            self._accessors[key] = value
            return
        object.__setattr__(self, key, value)

    async def connect_all(self) -> None:
        for name, accessor in self._accessors.items():
            self._logger.info("connecting accessor", accessor=name)
            await accessor.connect()
            self._logger.info("accessor connected", accessor=name)

    async def disconnect_all(self) -> None:
        for name, accessor in reversed(list(self._accessors.items())):
            self._logger.info("disconnecting accessor", accessor=name)
            await accessor.disconnect()
            self._logger.info("accessor disconnected", accessor=name)
