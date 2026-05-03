import json
from collections.abc import AsyncGenerator

import httpx

from app.base.manager import BaseManager
from app.chat.domain.enums import MessageRole
from app.chat.domain.models import ChatMessage
from app.common.config import StaticConfig
from app.common.sse import SSEEventType, sse_event
from app.rag.accessors.retriever import SearchResult
from app.rag.config import RAGConfig


class RAGManager(BaseManager):
    """Orchestrates the full RAG cycle: embed -> search -> prompt -> stream."""

    def _rag_config(self) -> RAGConfig:
        return RAGConfig.from_settings(self.store.settings.config)

    async def ask(
        self,
        question: str,
        chat_history: list[ChatMessage] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Yield SSE-formatted events: token, sources, done."""
        history = chat_history or []

        try:
            query_vector = await self.store.embedder.embed_text(question)
        except (RuntimeError, httpx.HTTPStatusError, httpx.TimeoutException):
            self.logger.exception("failed to embed question")
            yield sse_event(
                SSEEventType.ERROR,
                "Ошибка при обработке вопроса.",
            )
            yield sse_event(SSEEventType.DONE, "")
            return

        rag_cfg = self._rag_config()

        try:
            results = await self.store.retriever.search(
                query_vector=query_vector,
                top_k=rag_cfg.top_k,
                score_threshold=rag_cfg.score_threshold,
            )
        except Exception:  # noqa: BLE001 — qdrant client exceptions
            self.logger.exception("failed to search in qdrant")
            yield sse_event(
                SSEEventType.ERROR,
                "Ошибка при поиске в базе знаний.",
            )
            yield sse_event(SSEEventType.DONE, "")
            return

        if not results:
            yield sse_event(
                SSEEventType.NO_DATA,
                "К сожалению, в базе знаний нет информации "
                "для ответа на этот вопрос. "
                "Попробуйте переформулировать вопрос.",
            )
            yield sse_event(SSEEventType.DONE, "")
            return

        context = _build_context(results)
        messages = _build_messages(context, history, question)

        try:
            serialized = [m.model_dump() for m in messages]
            async for token in self.store.llm.stream_completion(
                serialized,
            ):
                yield sse_event(SSEEventType.TOKEN, token)
        except (RuntimeError, httpx.HTTPStatusError, httpx.TimeoutException):
            self.logger.exception("failed during LLM streaming")
            yield sse_event(
                SSEEventType.ERROR,
                "Ошибка при генерации ответа.",
            )
            yield sse_event(SSEEventType.DONE, "")
            return

        sources = [
            {
                "document_title": r.document_title,
                "content": r.content[:200],
                "score": round(r.score, 3),
            }
            for r in results
        ]
        yield sse_event(
            SSEEventType.SOURCES,
            json.dumps(sources, ensure_ascii=False),
        )
        yield sse_event(SSEEventType.DONE, "")


def _build_context(results: list[SearchResult]) -> str:
    parts: list[str] = []
    for i, r in enumerate(results, 1):
        parts.append(
            f"[Источник {i}: {r.document_title}]\n{r.content}",
        )
    return "\n\n".join(parts)


def _build_messages(
    context: str,
    history: list[ChatMessage],
    question: str,
) -> list[ChatMessage]:
    system_content = (
        f"{StaticConfig.SYSTEM_PROMPT}"
        f"\n\nКонтекст из базы знаний:\n\n{context}"
    )
    messages: list[ChatMessage] = [
        ChatMessage(role=MessageRole.SYSTEM, content=system_content),
    ]
    messages.extend(history)
    messages.append(
        ChatMessage(role=MessageRole.USER, content=question),
    )
    return messages
