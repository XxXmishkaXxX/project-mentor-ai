import json
from collections.abc import AsyncGenerator

from app.base.manager import BaseManager
from app.common.config import StaticConfig
from app.rag.accessors.retriever import SearchResult
from app.rag.config import RAGConfig


class RAGManager(BaseManager):
    """Orchestrates the full RAG cycle: embed -> search -> prompt -> stream."""

    def _rag_config(self) -> RAGConfig:
        return RAGConfig.from_settings(self.store.settings.config)

    async def ask(
        self,
        question: str,
        chat_history: list[dict[str, str]] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Yield SSE-formatted events: token, sources, done."""
        history = chat_history or []

        try:
            query_vector = await self.store.embedder.embed_text(question)
        except Exception:
            self.logger.exception("failed to embed question")
            yield _sse_event("error", "Ошибка при обработке вопроса.")
            yield _sse_event("done", "")
            return

        rag_cfg = self._rag_config()

        try:
            results = await self.store.retriever.search(
                query_vector=query_vector,
                top_k=rag_cfg.top_k,
                score_threshold=rag_cfg.score_threshold,
            )
        except Exception:
            self.logger.exception("failed to search in qdrant")
            yield _sse_event("error", "Ошибка при поиске в базе знаний.")
            yield _sse_event("done", "")
            return

        if not results:
            yield _sse_event(
                "no_data",
                "К сожалению, в базе знаний нет информации "
                "для ответа на этот вопрос. "
                "Попробуйте переформулировать вопрос.",
            )
            yield _sse_event("done", "")
            return

        context = _build_context(results)
        messages = _build_messages(context, history, question)

        try:
            async for token in self.store.llm.stream_completion(messages):
                yield _sse_event("token", token)
        except Exception:
            self.logger.exception("failed during LLM streaming")
            yield _sse_event("error", "Ошибка при генерации ответа.")
            yield _sse_event("done", "")
            return

        sources = [
            {
                "document_title": r.document_title,
                "content": r.content[:200],
                "score": round(r.score, 3),
            }
            for r in results
        ]
        yield _sse_event("sources", json.dumps(sources, ensure_ascii=False))
        yield _sse_event("done", "")


def _build_context(results: list[SearchResult]) -> str:
    parts: list[str] = []
    for i, r in enumerate(results, 1):
        parts.append(
            f"[Источник {i}: {r.document_title}]\n{r.content}",
        )
    return "\n\n".join(parts)


def _build_messages(
    context: str,
    history: list[dict[str, str]],
    question: str,
) -> list[dict[str, str]]:
    system_content = (
        f"{StaticConfig.SYSTEM_PROMPT}\n\nКонтекст из базы знаний:\n\n{context}"
    )
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_content},
    ]

    for msg in history:
        role = msg.get("role")
        content = msg.get("content")
        if role and content is not None:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": question})
    return messages


def _sse_event(event: str, data: str) -> str:
    return f"event: {event}\ndata: {data}\n\n"
