from __future__ import annotations

import asyncio
import sys
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import click
import structlog
from sqlalchemy import delete, select
from sqlalchemy import update as sa_update

from app import global_store
from app.common.config import StaticConfig
from app.documents.db import DocumentModel
from app.rag.chunker import parse_file, split_into_chunks
from app.rag.config import RAGConfig
from app.store.store import Store

if TYPE_CHECKING:
    from app.global_.settings import Settings

logger = structlog.get_logger("seed_knowledge_base")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
KB_DIR = PROJECT_ROOT / "knowledge_base"


async def _seed(store: Store) -> None:
    if not store.is_rag_available:
        logger.error(
            "RAG is not configured (llm.api_base_url is empty). "
            "Cannot embed documents.",
        )
        sys.exit(1)

    if not KB_DIR.is_dir():
        logger.error("knowledge_base/ directory not found", path=str(KB_DIR))
        sys.exit(1)

    files = sorted(
        f
        for f in KB_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in StaticConfig.SUPPORTED_EXTENSIONS
    )

    if not files:
        logger.info("No supported files found in knowledge_base/", dir=str(KB_DIR))
        return

    logger.info("Found files to process", count=len(files))
    rag_cfg = RAGConfig.from_settings(store.settings.config)
    collection_ensured = False
    indexed = 0

    for file_path in files:
        rel_path = str(file_path.relative_to(PROJECT_ROOT))

        existing = await store.pg.scalar_one_or_none(
            select(DocumentModel).where(DocumentModel.file_path == rel_path),
        )
        if existing is not None and existing.status == "indexed":
            logger.info("Already indexed, skipping", file=rel_path)
            continue

        if existing is not None:
            logger.info(
                "Cleaning up partial state before re-index",
                file=rel_path,
                old_status=existing.status,
            )
            try:
                await store.retriever.delete_by_document(str(existing.id))
            except Exception:  # noqa: BLE001
                logger.warning("Could not clean Qdrant vectors", file=rel_path)
            await store.pg.execute(
                delete(DocumentModel).where(DocumentModel.id == existing.id),
            )

        logger.info("Processing", file=rel_path)
        try:
            content = parse_file(file_path)
            if not content.strip():
                logger.warning("Empty file, skipping", file=rel_path)
                continue

            chunks = split_into_chunks(
                content,
                chunk_size=rag_cfg.chunk_size,
                overlap=rag_cfg.chunk_overlap,
                file_name=file_path.name,
            )
            if not chunks:
                logger.warning("No chunks produced, skipping", file=rel_path)
                continue

            vectors = await store.embedder.embed_batch([c.text for c in chunks])
            if not vectors:
                logger.warning("Empty embeddings, skipping", file=rel_path)
                continue

            if not collection_ensured:
                await store.retriever.ensure_collection(len(vectors[0]))
                collection_ensured = True

            doc_id = str(uuid.uuid4())

            doc = DocumentModel(
                id=uuid.UUID(doc_id),
                filename=file_path.name,
                title=file_path.stem,
                file_path=rel_path,
                status="pending",
                chunk_count=len(chunks),
            )
            await store.pg.add_one(doc)

            await store.retriever.upsert_chunks(
                document_id=doc_id,
                chunks=chunks,
                vectors=vectors,
                document_title=file_path.stem,
            )

            await store.pg.execute(
                sa_update(DocumentModel)
                .where(DocumentModel.id == uuid.UUID(doc_id))
                .values(status="indexed"),
            )

            logger.info(
                "Indexed successfully",
                file=rel_path,
                chunks=len(chunks),
                document_id=doc_id,
            )
            indexed += 1

        except Exception:
            logger.exception("Failed to process", file=rel_path)

    logger.info("Seeding complete", indexed=indexed)


@click.command(name="seed_knowledge_base", help="Seed the knowledge base: parse → chunk → embed → Qdrant + PG")
@click.pass_obj
def seed_knowledge_base(settings: "Settings") -> None:
    """python -m app seed_knowledge_base"""

    async def _run() -> None:
        store = Store(settings)
        global_store.set(store)
        try:
            await store.connect_all()
            await _seed(store)
        finally:
            await store.disconnect_all()

    asyncio.run(_run())
