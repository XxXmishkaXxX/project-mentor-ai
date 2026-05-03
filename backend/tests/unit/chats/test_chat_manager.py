import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.chat.exceptions import ChatAccessDeniedError, ChatNotFoundError
from app.chat.manager import ChatManager
from app.common.sse import parse_sse, sse_event


@pytest.fixture
def chat_manager(mock_store: MagicMock) -> ChatManager:
    return ChatManager(mock_store)


def _make_chat(
    user_id: uuid.UUID,
    title: str | None = None,
) -> MagicMock:
    chat = MagicMock()
    chat.id = uuid.uuid4()
    chat.user_id = user_id
    chat.title = title
    chat.created_at = "2025-01-01T00:00:00Z"
    chat.updated_at = "2025-01-01T00:00:00Z"
    return chat


class TestGetOwnChat:
    async def test_not_found(
        self,
        chat_manager: ChatManager,
        mock_store: MagicMock,
    ):
        mock_store.chat_accessor.get_chat_by_id = AsyncMock(
            return_value=None,
        )

        with pytest.raises(ChatNotFoundError):
            await chat_manager._get_own_chat(uuid.uuid4(), uuid.uuid4())

    async def test_access_denied(
        self,
        chat_manager: ChatManager,
        mock_store: MagicMock,
    ):
        owner_id = uuid.uuid4()
        other_id = uuid.uuid4()
        chat = _make_chat(owner_id)

        mock_store.chat_accessor.get_chat_by_id = AsyncMock(
            return_value=chat,
        )

        with pytest.raises(ChatAccessDeniedError):
            await chat_manager._get_own_chat(chat.id, other_id)

    async def test_success(
        self,
        chat_manager: ChatManager,
        mock_store: MagicMock,
    ):
        user_id = uuid.uuid4()
        chat = _make_chat(user_id)

        mock_store.chat_accessor.get_chat_by_id = AsyncMock(
            return_value=chat,
        )

        result = await chat_manager._get_own_chat(chat.id, user_id)
        assert result.id == chat.id


class TestCreateChat:
    async def test_returns_response(
        self,
        chat_manager: ChatManager,
        mock_store: MagicMock,
    ):
        user_id = uuid.uuid4()
        chat = _make_chat(user_id)
        mock_store.chat_accessor.create_chat = AsyncMock(return_value=chat)

        result = await chat_manager.create_chat(user_id)

        assert result.id == chat.id
        mock_store.chat_accessor.create_chat.assert_called_once_with(user_id)


class TestSendMessageNoRAG:
    async def test_yields_error_when_rag_unavailable(
        self,
        chat_manager: ChatManager,
        mock_store: MagicMock,
    ):
        user_id = uuid.uuid4()
        chat = _make_chat(user_id)
        mock_store.chat_accessor.get_chat_by_id = AsyncMock(
            return_value=chat,
        )
        mock_store.chat_accessor.add_message = AsyncMock()
        mock_store.chat_accessor.get_recent_messages = AsyncMock(
            return_value=[],
        )
        mock_store.chat_accessor.update_chat = AsyncMock()
        mock_store.is_rag_available = False

        raw_events = []
        parsed_events = []
        async for event in chat_manager.send_message(
            chat.id,
            user_id,
            "Hello",
        ):
            raw_events.append(event)
            parsed = parse_sse(event)
            if parsed:
                parsed_events.append(parsed)

        assert parsed_events[0][0] == "error"
        assert sse_event("done", "") in raw_events
