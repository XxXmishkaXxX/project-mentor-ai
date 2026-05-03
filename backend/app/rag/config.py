from dataclasses import dataclass
from typing import Any

from app.global_.settings import path


@dataclass
class QdrantConfig:
    host: str = "localhost"
    port: int = 6333

    @classmethod
    def from_settings(cls, config: dict) -> "QdrantConfig":
        return cls(
            host=path(config, "qdrant", "host", default="localhost"),
            port=int(
                path(config, "qdrant", "port", default=6333),
            ),
        )


@dataclass
class LLMProviderConfig:
    api_key: str = ""
    api_base_url: str = ""
    model: str = ""
    embedding_model: str = ""

    @classmethod
    def from_settings(cls, config: dict) -> "LLMProviderConfig":
        return cls(
            api_key=path(config, "llm", "api_key", default=""),
            api_base_url=path(config, "llm", "api_base_url", default=""),
            model=path(config, "llm", "model", default=""),
            embedding_model=path(
                config,
                "llm",
                "embedding_model",
                default="",
            ),
        )


@dataclass
class RAGConfig:
    top_k: int = 5
    score_threshold: float = 0.15
    chunk_size: int = 512
    chunk_overlap: int = 64

    @classmethod
    def from_settings(cls, config: dict) -> "RAGConfig":
        return cls(
            top_k=int(path(config, "rag", "top_k", default=5)),
            score_threshold=float(
                path(config, "rag", "score_threshold", default=0.15),
            ),
            chunk_size=int(
                path(config, "rag", "chunk_size", default=512),
            ),
            chunk_overlap=int(
                path(config, "rag", "chunk_overlap", default=64),
            ),
        )


def is_rag_configured(config: dict[str, Any]) -> bool:
    """Check whether LLM API base URL is set (minimum for RAG to work)."""
    return bool(path(config, "llm", "api_base_url", default=""))
