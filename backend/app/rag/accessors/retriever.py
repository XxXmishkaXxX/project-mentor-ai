import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.base.accessor import BaseAccessor
from app.common.config import StaticConfig
from app.rag.config import QdrantConfig, RAGConfig

if TYPE_CHECKING:
    from app.rag.chunker import Chunk


@dataclass
class SearchResult:
    document_id: str
    document_title: str
    content: str
    chunk_index: int
    score: float


class RetrieverAccessor(BaseAccessor):
    async def connect(self) -> None:
        config = QdrantConfig.from_settings(self.store.settings.config)
        self._rag_config = RAGConfig.from_settings(
            self.store.settings.config,
        )
        self._client = AsyncQdrantClient(
            host=config.host,
            port=config.port,
        )
        self.logger.info(
            "retriever connected",
            host=config.host,
            port=config.port,
        )

    @property
    def client(self) -> AsyncQdrantClient:
        return self._client

    async def disconnect(self) -> None:
        if hasattr(self, "_client"):
            await self._client.close()

    async def ensure_collection(
        self,
        vector_size: int,
    ) -> None:
        name = StaticConfig.QDRANT_COLLECTION_NAME
        collections = await self._client.get_collections()
        existing = {c.name for c in collections.collections}

        if name in existing:
            info = await self._client.get_collection(name)
            vectors_cfg = info.config.params.vectors
            actual_size = (
                vectors_cfg.size
                if isinstance(vectors_cfg, VectorParams)
                else None
            )
            if actual_size is not None and actual_size != vector_size:
                self.logger.error(
                    "collection vector_size mismatch",
                    name=name,
                    expected=vector_size,
                    actual=actual_size,
                )
                msg = (
                    f"Collection '{name}' exists with "
                    f"vector_size={actual_size}, expected {vector_size}"
                )
                raise ValueError(msg)
            self.logger.info("collection already exists", name=name)
            return

        await self._client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
                on_disk=True,
            ),
        )
        self.logger.info(
            "collection created",
            name=name,
            vector_size=vector_size,
        )

    async def upsert_chunks(
        self,
        document_id: str,
        chunks: list["Chunk"],
        vectors: list[list[float]],
        document_title: str = "",
    ) -> None:
        name = StaticConfig.QDRANT_COLLECTION_NAME
        points = [
            PointStruct(
                id=_point_id(document_id, i),
                vector=vector,
                payload={
                    "document_id": document_id,
                    "chunk_index": i,
                    "content": chunk.text,
                    "document_title": document_title,
                    "metadata": chunk.metadata,
                },
            )
            for i, (chunk, vector) in enumerate(
                zip(chunks, vectors, strict=True),
            )
        ]

        await self._client.upsert(
            collection_name=name,
            points=points,
        )
        self.logger.info(
            "chunks upserted",
            document_id=document_id,
            count=len(points),
        )

    async def delete_by_document(self, document_id: str) -> None:
        name = StaticConfig.QDRANT_COLLECTION_NAME
        await self._client.delete(
            collection_name=name,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id),
                        ),
                    ],
                ),
            ),
        )
        self.logger.info(
            "chunks deleted by document",
            document_id=document_id,
        )

    async def search(
        self,
        query_vector: list[float],
        top_k: int | None = None,
        score_threshold: float | None = None,
    ) -> list[SearchResult]:
        k = top_k if top_k is not None else self._rag_config.top_k
        threshold = (
            score_threshold
            if score_threshold is not None
            else self._rag_config.score_threshold
        )

        response = await self._client.query_points(
            collection_name=StaticConfig.QDRANT_COLLECTION_NAME,
            query=query_vector,
            limit=k,
            score_threshold=threshold,
        )

        search_results: list[SearchResult] = []
        for hit in response.points:
            payload = hit.payload or {}
            document_id = payload.get("document_id")
            content = payload.get("content")
            if document_id is None or content is None:
                self.logger.warning(
                    "skipping hit with missing payload fields",
                    point_id=hit.id,
                )
                continue
            search_results.append(
                SearchResult(
                    document_id=document_id,
                    document_title=payload.get("document_title", ""),
                    content=content,
                    chunk_index=payload.get("chunk_index", 0),
                    score=hit.score,
                ),
            )
        return search_results


def _point_id(document_id: str, chunk_index: int) -> str:
    """Deterministic point ID (UUID5) for upsert idempotency."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{document_id}:{chunk_index}"))
