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
class QwenConfig:
    api_key: str = ""
    api_base_url: str = ""
    model: str = "qwen-3.6"
    embedding_model: str = "qwen-embedding"

    @classmethod
    def from_settings(cls, config: dict) -> "QwenConfig":
        return cls(
            api_key=path(config, "qwen", "api_key", default=""),
            api_base_url=path(config, "qwen", "api_base_url", default=""),
            model=path(config, "qwen", "model", default="qwen-3.6"),
            embedding_model=path(
                config,
                "qwen",
                "embedding_model",
                default="qwen-embedding",
            ),
        )


@dataclass
class RAGConfig:
    top_k: int = 5
    score_threshold: float = 0.7
    chunk_size: int = 512
    chunk_overlap: int = 64

    @classmethod
    def from_settings(cls, config: dict) -> "RAGConfig":
        return cls(
            top_k=int(path(config, "rag", "top_k", default=5)),
            score_threshold=float(
                path(config, "rag", "score_threshold", default=0.7),
            ),
            chunk_size=int(
                path(config, "rag", "chunk_size", default=512),
            ),
            chunk_overlap=int(
                path(config, "rag", "chunk_overlap", default=64),
            ),
        )


def is_rag_configured(config: dict[str, Any]) -> bool:
    """Check whether Qwen API base URL is set (minimum for RAG to work)."""
    return bool(path(config, "qwen", "api_base_url", default=""))
