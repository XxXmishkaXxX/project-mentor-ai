from unittest.mock import AsyncMock, MagicMock

from app.chat.domain.enums import MessageRole
from app.chat.domain.models import ChatMessage
from app.common.sse import SSEEventType, parse_sse, sse_event
from app.rag.accessors.retriever import SearchResult
from app.rag.manager import RAGManager


async def _collect_raw(gen) -> list[str]:
    """Consume an SSE async generator, return raw event strings."""
    return [raw async for raw in gen]


class TestRAGManagerAsk:
    async def test_embed_failure_yields_error(
        self,
        rag_manager: RAGManager,
        mock_store: MagicMock,
    ):
        mock_store.embedder.embed_text = AsyncMock(
            side_effect=RuntimeError("embed failed"),
        )

        raw = await _collect_raw(rag_manager.ask("test question"))
        parsed = [p for r in raw if (p := parse_sse(r))]

        assert len(parsed) == 2
        assert parsed[0].event == SSEEventType.ERROR
        assert parsed[1].event == SSEEventType.DONE

    async def test_retriever_failure_yields_error(
        self,
        rag_manager: RAGManager,
        mock_store: MagicMock,
    ):
        mock_store.embedder.embed_text = AsyncMock(
            return_value=[0.1, 0.2, 0.3],
        )
        mock_store.retriever.search = AsyncMock(
            side_effect=RuntimeError("qdrant down"),
        )

        raw = await _collect_raw(rag_manager.ask("test question"))
        parsed = [p for r in raw if (p := parse_sse(r))]

        assert parsed[0].event == SSEEventType.ERROR
        assert sse_event(SSEEventType.DONE, "") in raw

    async def test_no_results_yields_no_data(
        self,
        rag_manager: RAGManager,
        mock_store: MagicMock,
    ):
        mock_store.embedder.embed_text = AsyncMock(
            return_value=[0.1, 0.2, 0.3],
        )
        mock_store.retriever.search = AsyncMock(return_value=[])

        raw = await _collect_raw(rag_manager.ask("test question"))
        parsed = [p for r in raw if (p := parse_sse(r))]

        assert parsed[0].event == SSEEventType.NO_DATA
        assert sse_event(SSEEventType.DONE, "") in raw

    async def test_successful_flow_yields_tokens_sources_done(
        self,
        rag_manager: RAGManager,
        mock_store: MagicMock,
    ):
        mock_store.embedder.embed_text = AsyncMock(
            return_value=[0.1, 0.2, 0.3],
        )

        search_results = [
            SearchResult(
                document_id="doc1",
                document_title="Test Doc",
                content="Some relevant content here.",
                chunk_index=0,
                score=0.9,
            ),
        ]
        mock_store.retriever.search = AsyncMock(
            return_value=search_results,
        )

        async def fake_stream(messages):
            yield "Hello"
            yield " world"

        mock_store.llm.stream_completion = fake_stream

        raw = await _collect_raw(rag_manager.ask("test question"))
        parsed = [p for r in raw if (p := parse_sse(r))]

        event_types = [e.event for e in parsed]
        assert SSEEventType.TOKEN in event_types
        assert SSEEventType.SOURCES in event_types
        assert sse_event(SSEEventType.DONE, "") in raw

        tokens = [e.data for e in parsed if e.event == SSEEventType.TOKEN]
        assert "Hello" in tokens
        assert " world" in tokens

    async def test_llm_failure_yields_error(
        self,
        rag_manager: RAGManager,
        mock_store: MagicMock,
    ):
        mock_store.embedder.embed_text = AsyncMock(
            return_value=[0.1, 0.2, 0.3],
        )
        mock_store.retriever.search = AsyncMock(
            return_value=[
                SearchResult(
                    document_id="doc1",
                    document_title="Doc",
                    content="content",
                    chunk_index=0,
                    score=0.8,
                ),
            ],
        )

        async def failing_stream(messages):
            raise RuntimeError("LLM failed")
            yield  # noqa: RET503 — makes it an async generator

        mock_store.llm.stream_completion = failing_stream

        raw = await _collect_raw(rag_manager.ask("question"))
        parsed = [p for r in raw if (p := parse_sse(r))]

        assert any(e.event == SSEEventType.ERROR for e in parsed)
        assert sse_event(SSEEventType.DONE, "") in raw

    async def test_chat_history_is_passed_through(
        self,
        rag_manager: RAGManager,
        mock_store: MagicMock,
    ):
        mock_store.embedder.embed_text = AsyncMock(
            return_value=[0.1, 0.2],
        )
        mock_store.retriever.search = AsyncMock(
            return_value=[
                SearchResult(
                    document_id="doc1",
                    document_title="Doc",
                    content="content",
                    chunk_index=0,
                    score=0.8,
                ),
            ],
        )

        captured_messages = []

        async def capturing_stream(messages):
            captured_messages.extend(messages)
            yield "ok"

        mock_store.llm.stream_completion = capturing_stream

        history = [
            ChatMessage(
                role=MessageRole.USER,
                content="prev question",
            ),
            ChatMessage(
                role=MessageRole.ASSISTANT,
                content="prev answer",
            ),
        ]

        await _collect_raw(
            rag_manager.ask("new question", chat_history=history),
        )

        roles = [m["role"] for m in captured_messages]
        assert MessageRole.SYSTEM in roles
        assert MessageRole.USER in roles
        user_contents = [
            m["content"]
            for m in captured_messages
            if m["role"] == MessageRole.USER
        ]
        assert "prev question" in user_contents
        assert "new question" in user_contents
