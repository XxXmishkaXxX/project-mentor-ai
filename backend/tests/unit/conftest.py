from unittest.mock import AsyncMock, MagicMock

import pytest
from cashews import cache

from app.global_.settings import Settings


@pytest.fixture(scope="session")
async def _setup_mem_cache():
    cache.setup("mem://")


@pytest.fixture
def mock_store(settings: Settings) -> MagicMock:
    store = MagicMock()
    store.settings = settings
    store.pg.is_connected = False

    store.user_accessor = AsyncMock()
    store.session_accessor = AsyncMock()
    store.chat_accessor = AsyncMock()

    store.embedder = AsyncMock()
    store.retriever = AsyncMock()
    store.llm = AsyncMock()

    store.is_rag_available = True

    store.user_manager = MagicMock()
    store.auth_manager = MagicMock()
    store.chat_manager = MagicMock()

    return store
