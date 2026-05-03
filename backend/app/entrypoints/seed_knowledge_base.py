import uuid
from pathlib import Path

import click
from sqlalchemy import delete, select
from sqlalchemy import update as sa_update

from app.common.config import StaticConfig
from app.documents.db import DocumentModel
from app.global_.settings import path as cfg_path
from app.rag.chunker import parse_file, split_into_chunks
from app.rag.config import RAGConfig

from . import BaseCommand


class SeedKnowledgeBase(BaseCommand):
    """
    python -m app seed_knowledge_base
    python -m app seed_knowledge_base --dir /path/to/custom/kb
    """

    name = "seed_knowledge_base"
    help = "Seed the knowledge base: parse → chunk → embed → Qdrant + PG"

    @classmethod
    def click_options(cls) -> list:
        return [
            click.option(
                "--dir",
                "kb_dir",
                type=click.Path(exists=True, file_okay=False, path_type=Path),
                default=None,
                help="Path to knowledge_base directory "
                "(default: from config or ./knowledge_base)",
            ),
        ]

    def _resolve_kb_dir(self, kb_dir: Path | None) -> Path:
        if kb_dir is not None:
            return kb_dir
        configured = cfg_path(
            self.store.settings.config,
            "app",
            "knowledge_base_dir",
            default="knowledge_base",
        )
        resolved = Path(configured)
        if not resolved.is_absolute():
            resolved = Path.cwd() / resolved
        return resolved

    async def execute(self, kb_dir: Path | None = None, **_kwargs) -> None:
        kb_dir = self._resolve_kb_dir(kb_dir)

        if not self.store.is_rag_available:
            self.logger.error(
                "RAG is not configured (llm.api_base_url is empty). "
                "Cannot embed documents.",
            )
            return

        if not kb_dir.is_dir():
            self.logger.error(
                "knowledge_base/ directory not found", path=str(kb_dir)
            )
            return

        files = sorted(
            f
            for f in kb_dir.iterdir()
            if f.is_file()
            and f.suffix.lower() in StaticConfig.SUPPORTED_EXTENSIONS
        )

        if not files:
            self.logger.info("No supported files found", dir=str(kb_dir))
            return

        self.logger.info("Found files to process", count=len(files))
        rag_cfg = RAGConfig.from_settings(self.store.settings.config)
        collection_ensured = False
        indexed = 0

        for file_path in files:
            rel_path = str(file_path.relative_to(kb_dir.parent))
            indexed += await self._process_file(
                file_path,
                rel_path,
                rag_cfg,
                collection_ensured,
            )
            if not collection_ensured and indexed > 0:
                collection_ensured = True

        self.logger.info("Seeding complete", indexed=indexed)

    async def _process_file(
        self,
        file_path: Path,
        rel_path: str,
        rag_cfg: RAGConfig,
        collection_ensured: bool,
    ) -> int:
        existing = await self.store.pg.scalar_one_or_none(
            select(DocumentModel).where(DocumentModel.file_path == rel_path),
        )
        if existing is not None and existing.status == "indexed":
            self.logger.info("Already indexed, skipping", file=rel_path)
            return 0

        if existing is not None:
            self.logger.info(
                "Cleaning up partial state before re-index",
                file=rel_path,
                old_status=existing.status,
            )
            try:
                await self.store.retriever.delete_by_document(str(existing.id))
            except Exception:  # noqa: BLE001
                self.logger.warning(
                    "Could not clean Qdrant vectors", file=rel_path
                )
            await self.store.pg.execute(
                delete(DocumentModel).where(DocumentModel.id == existing.id),
            )

        self.logger.info("Processing", file=rel_path)
        try:
            content = parse_file(file_path)
            if not content.strip():
                self.logger.warning("Empty file, skipping", file=rel_path)
                return 0

            chunks = split_into_chunks(
                content,
                chunk_size=rag_cfg.chunk_size,
                overlap=rag_cfg.chunk_overlap,
                file_name=file_path.name,
            )
            if not chunks:
                self.logger.warning(
                    "No chunks produced, skipping", file=rel_path
                )
                return 0

            vectors = await self.store.embedder.embed_batch(
                [c.text for c in chunks]
            )
            if not vectors:
                self.logger.warning("Empty embeddings, skipping", file=rel_path)
                return 0

            if not collection_ensured:
                await self.store.retriever.ensure_collection(len(vectors[0]))

            doc_id = str(uuid.uuid4())

            doc = DocumentModel(
                id=uuid.UUID(doc_id),
                filename=file_path.name,
                title=file_path.stem,
                file_path=rel_path,
                status="pending",
                chunk_count=len(chunks),
            )
            await self.store.pg.add_one(doc)

            await self.store.retriever.upsert_chunks(
                document_id=doc_id,
                chunks=chunks,
                vectors=vectors,
                document_title=file_path.stem,
            )

            await self.store.pg.execute(
                sa_update(DocumentModel)
                .where(DocumentModel.id == uuid.UUID(doc_id))
                .values(status="indexed"),
            )

            self.logger.info(
                "Indexed successfully",
                file=rel_path,
                chunks=len(chunks),
                document_id=doc_id,
            )
            return 1

        except Exception:
            self.logger.exception("Failed to process", file=rel_path)
            return 0


seed_knowledge_base = SeedKnowledgeBase.command
