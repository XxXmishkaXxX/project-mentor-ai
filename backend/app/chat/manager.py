import json
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

from app.base.manager import BaseManager
from app.chat.db import ChatModel, MessageModel
from app.chat.domain.schemas import (
    ChatResponse,
    MessageListResponse,
    MessageResponse,
)
from app.chat.exceptions import ChatNotFoundError
from app.common.sse import parse_sse, sse_event

MAX_TITLE_LENGTH = 100
HISTORY_WINDOW = 10


class ChatManager(BaseManager):
    def _to_chat_response(self, chat: ChatModel) -> ChatResponse:
        return ChatResponse(
            id=chat.id,
            title=chat.title,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
        )

    def _to_message_response(self, msg: MessageModel) -> MessageResponse:
        return MessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            sources=msg.sources,
            created_at=msg.created_at,
        )

    async def _get_own_chat(
        self,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ChatModel:
        chat = await self.store.chat_accessor.get_chat_by_id(chat_id)
        if chat is None or chat.user_id != user_id:
            raise ChatNotFoundError()
        return chat

    async def create_chat(self, user_id: uuid.UUID) -> ChatResponse:
        chat = await self.store.chat_accessor.create_chat(user_id)
        return self._to_chat_response(chat)

    async def get_chats(self, user_id: uuid.UUID) -> list[ChatResponse]:
        chats = await self.store.chat_accessor.get_chats_by_user(user_id)
        return [self._to_chat_response(c) for c in chats]

    async def get_chat(
        self,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ChatResponse:
        chat = await self._get_own_chat(chat_id, user_id)
        return self._to_chat_response(chat)

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
            messages=[self._to_message_response(m) for m in messages],
            total=total,
        )

    async def send_message(
        self,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str,
    ) -> AsyncGenerator[str, None]:
        chat = await self._get_own_chat(chat_id, user_id)

        await self.store.chat_accessor.add_message(
            chat_id=chat_id,
            role="user",
            content=content,
        )

        if chat.title is None:
            title = content[:MAX_TITLE_LENGTH]
            await self.store.chat_accessor.update_chat(
                chat_id,
                title=title,
            )

        history_msgs = await self.store.chat_accessor.get_recent_messages(
            chat_id,
            limit=HISTORY_WINDOW,
        )
        chat_history = [
            {"role": m.role, "content": m.content} for m in history_msgs[:-1]
        ]

        if not self.store.is_rag_available:
            yield sse_event(
                "error",
                "RAG pipeline не настроен. Обратитесь к администратору.",
            )
            yield sse_event("done", "")
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

            event_type, data = parsed
            if event_type == "token":
                full_answer.append(data)
            elif event_type == "error":
                has_error = True
            elif event_type == "sources":
                try:
                    sources_data = json.loads(data)
                except json.JSONDecodeError:
                    self.logger.warning("failed to parse sources JSON")

        assistant_content = "".join(full_answer)
        if assistant_content and not has_error:
            try:
                await self.store.chat_accessor.add_message(
                    chat_id=chat_id,
                    role="assistant",
                    content=assistant_content,
                    sources=sources_data,
                )
            except Exception:
                self.logger.exception(
                    "failed to save assistant message",
                    chat_id=str(chat_id),
                )

        try:
            await self.store.chat_accessor.update_chat(
                chat_id,
                updated_at=datetime.now(timezone.utc),
            )
        except Exception:
            self.logger.exception(
                "failed to update chat timestamp",
                chat_id=str(chat_id),
            )
