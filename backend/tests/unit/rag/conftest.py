from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from app.rag.config import RAGConfig
from app.rag.manager import RAGManager


@pytest.fixture
def rag_config() -> RAGConfig:
    return RAGConfig(
        top_k=3,
        score_threshold=0.5,
        chunk_size=256,
        chunk_overlap=32,
    )


@pytest.fixture
def rag_manager(mock_store: MagicMock, rag_config: RAGConfig) -> RAGManager:
    mock_store.settings.config = {
        "rag": {
            "top_k": rag_config.top_k,
            "score_threshold": rag_config.score_threshold,
            "chunk_size": rag_config.chunk_size,
            "chunk_overlap": rag_config.chunk_overlap,
        },
    }
    return RAGManager(mock_store)
