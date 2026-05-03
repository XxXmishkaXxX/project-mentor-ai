import uuid
from typing import Any

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.base.accessor import BaseAccessor
from app.chat.db import ChatModel, MessageModel
from app.chat.domain.enums import MessageRole
from app.chat.domain.models import Chat, Message


class ChatAccessor(BaseAccessor):
    async def create_chat(self, user_id: uuid.UUID) -> Chat:
        stmt = (
            pg_insert(ChatModel)
            .values(user_id=user_id)
            .returning(ChatModel)
        )
        result = await self.store.pg.execute(stmt)
        return Chat.from_db(result.scalar_one())

    async def get_chats_by_user(self, user_id: uuid.UUID) -> list[Chat]:
        stmt = (
            select(ChatModel)
            .where(ChatModel.user_id == user_id)
            .order_by(ChatModel.updated_at.desc())
        )
        rows = await self.store.pg.scalars_all(stmt)
        return [Chat.from_db(r) for r in rows]

    async def get_chat_by_id(self, chat_id: uuid.UUID) -> Chat | None:
        row = await self.store.pg.scalar_one_or_none(
            select(ChatModel).where(ChatModel.id == chat_id),
        )
        return Chat.from_db(row) if row else None

    async def get_chat_by_owner(
        self,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Chat | None:
        row = await self.store.pg.scalar_one_or_none(
            select(ChatModel).where(
                ChatModel.id == chat_id,
                ChatModel.user_id == user_id,
            ),
        )
        return Chat.from_db(row) if row else None

    async def delete_chat(self, chat_id: uuid.UUID) -> None:
        await self.store.pg.execute(
            delete(ChatModel).where(ChatModel.id == chat_id),
        )

    async def update_chat(
        self,
        chat_id: uuid.UUID,
        **values: Any,
    ) -> Chat | None:
        if not values:
            return await self.get_chat_by_id(chat_id)
        stmt = (
            update(ChatModel)
            .where(ChatModel.id == chat_id)
            .values(**values)
            .returning(ChatModel)
        )
        result = await self.store.pg.execute(stmt)
        row = result.scalar_one_or_none()
        return Chat.from_db(row) if row else None

    async def add_message(
        self,
        *,
        chat_id: uuid.UUID,
        role: MessageRole,
        content: str,
        sources: list[dict] | None = None,
    ) -> Message:
        stmt = (
            pg_insert(MessageModel)
            .values(
                chat_id=chat_id,
                role=role,
                content=content,
                sources=sources,
            )
            .returning(MessageModel)
        )
        result = await self.store.pg.execute(stmt)
        return Message.from_db(result.scalar_one())

    async def get_messages(
        self,
        chat_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> list[Message]:
        stmt = (
            select(MessageModel)
            .where(MessageModel.chat_id == chat_id)
            .order_by(MessageModel.created_at.asc(), MessageModel.id.asc())
            .offset(offset)
            .limit(limit)
        )
        rows = await self.store.pg.scalars_all(stmt)
        return [Message.from_db(r) for r in rows]

    async def count_messages(self, chat_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(MessageModel)
            .where(MessageModel.chat_id == chat_id)
        )
        return await self.store.pg.scalar_one(stmt)

    async def get_recent_messages(
        self,
        chat_id: uuid.UUID,
        limit: int = 10,
    ) -> list[Message]:
        stmt = (
            select(MessageModel)
            .where(MessageModel.chat_id == chat_id)
            .order_by(MessageModel.created_at.desc(), MessageModel.id.desc())
            .limit(limit)
        )
        rows = await self.store.pg.scalars_all(stmt)
        return [Message.from_db(r) for r in reversed(rows)]
