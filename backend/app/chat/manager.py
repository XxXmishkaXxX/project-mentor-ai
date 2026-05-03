import json
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError

from app.base.decorators import with_transaction
from app.base.manager import BaseManager
from app.chat.domain.enums import MessageRole
from app.chat.domain.models import Chat, ChatMessage
from app.chat.domain.schemas import (
    ChatResponse,
    MessageListResponse,
    MessageResponse,
)
from app.chat.exceptions import ChatNotFoundError
from app.common.config import StaticConfig
from app.common.sse import SSEEventType, parse_sse, sse_event


class ChatManager(BaseManager):
    async def _get_own_chat(
        self,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Chat:
        chat = await self.store.chat_accessor.get_chat_by_owner(
            chat_id,
            user_id,
        )
        if chat is None:
            raise ChatNotFoundError()
        return chat

    async def create_chat(self, user_id: uuid.UUID) -> ChatResponse:
        chat = await self.store.chat_accessor.create_chat(user_id)
        return ChatResponse.from_model(chat)

    async def get_chats(self, user_id: uuid.UUID) -> list[ChatResponse]:
        chats = await self.store.chat_accessor.get_chats_by_user(user_id)
        return [ChatResponse.from_model(c) for c in chats]

    async def get_chat(
        self,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ChatResponse:
        chat = await self._get_own_chat(chat_id, user_id)
        return ChatResponse.from_model(chat)

    async def delete_chat(
        self,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        await self._get_own_chat(chat_id, user_id)
        await self.store.chat_accessor.delete_chat(chat_id)

    async def get_messages(
        self,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> MessageListResponse:
        await self._get_own_chat(chat_id, user_id)
        messages = await self.store.chat_accessor.get_messages(
            chat_id,
            offset=offset,
            limit=limit,
        )
        total = await self.store.chat_accessor.count_messages(chat_id)
        return MessageListResponse(
            messages=[MessageResponse.from_model(m) for m in messages],
            total=total,
        )

    async def send_message(
        self,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str,
    ) -> AsyncGenerator[str, None]:
        chat = await self._get_own_chat(chat_id, user_id)

        await self._save_user_message(chat, content)

        history_msgs = await self.store.chat_accessor.get_recent_messages(
            chat_id,
            limit=StaticConfig.CHAT_HISTORY_WINDOW,
        )
        chat_history = [
            ChatMessage(role=m.role, content=m.content)
            for m in history_msgs[:-1]
        ]

        if not self.store.is_rag_available:
            yield sse_event(
                SSEEventType.ERROR,
                "RAG pipeline не настроен. "
                "Обратитесь к администратору.",
            )
            yield sse_event(SSEEventType.DONE, "")
            return

        full_answer: list[str] = []
        sources_data: list[dict] | None = None
        has_error = False

        async for event in self.store.rag_manager.ask(
            content,
            chat_history=chat_history,
        ):
            yield event

            parsed = parse_sse(event)
            if parsed is None:
                continue

            if parsed.event == SSEEventType.TOKEN:
                full_answer.append(parsed.data)
            elif parsed.event == SSEEventType.ERROR:
                has_error = True
            elif parsed.event == SSEEventType.SOURCES:
                try:
                    sources_data = json.loads(parsed.data)
                except json.JSONDecodeError:
                    self.logger.warning(
                        "failed to parse sources JSON",
                    )

        assistant_content = "".join(full_answer)
        if assistant_content and not has_error:
            try:
                await self._save_assistant_message(
                    chat_id,
                    assistant_content,
                    sources_data,
                )
            except SQLAlchemyError:
                self.logger.exception(
                    "failed to save assistant message",
                    chat_id=str(chat_id),
                )

    @with_transaction
    async def _save_user_message(
        self,
        chat: Chat,
        content: str,
    ) -> None:
        await self.store.chat_accessor.add_message(
            chat_id=chat.id,
            role=MessageRole.USER,
            content=content,
        )
        if chat.title is None:
            title = content[: StaticConfig.MAX_CHAT_TITLE_LENGTH]
            await self.store.chat_accessor.update_chat(
                chat.id,
                title=title,
            )

    @with_transaction
    async def _save_assistant_message(
        self,
        chat_id: uuid.UUID,
        content: str,
        sources: list[dict] | None,
    ) -> None:
        await self.store.chat_accessor.add_message(
            chat_id=chat_id,
            role=MessageRole.ASSISTANT,
            content=content,
            sources=sources,
        )
        await self.store.chat_accessor.update_chat(
            chat_id,
            updated_at=datetime.now(timezone.utc),
        )
