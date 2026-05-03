import uuid

from sqlalchemy import delete, func, select, update

from app.base.accessor import BaseAccessor
from app.chat.db import ChatModel, MessageModel


class ChatAccessor(BaseAccessor):
    async def create_chat(self, user_id: uuid.UUID) -> ChatModel:
        chat = ChatModel(user_id=user_id)
        return await self.store.pg.add_one(chat)

    async def get_chats_by_user(self, user_id: uuid.UUID) -> list[ChatModel]:
        stmt = (
            select(ChatModel)
            .where(ChatModel.user_id == user_id)
            .order_by(ChatModel.updated_at.desc())
        )
        return await self.store.pg.scalars_all(stmt)

    async def get_chat_by_id(self, chat_id: uuid.UUID) -> ChatModel | None:
        stmt = select(ChatModel).where(ChatModel.id == chat_id)
        return await self.store.pg.scalar_one_or_none(stmt)

    async def delete_chat(self, chat_id: uuid.UUID) -> None:
        stmt = delete(ChatModel).where(ChatModel.id == chat_id)
        await self.store.pg.execute(stmt)

    async def update_chat(
        self,
        chat_id: uuid.UUID,
        **kwargs: object,
    ) -> ChatModel | None:
        if not kwargs:
            return await self.get_chat_by_id(chat_id)
        stmt = (
            update(ChatModel)
            .where(ChatModel.id == chat_id)
            .values(**kwargs)
            .returning(ChatModel)
        )
        async with self.store.pg.session() as session:
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar_one_or_none()

    async def add_message(
        self,
        *,
        chat_id: uuid.UUID,
        role: str,
        content: str,
        sources: list[dict] | None = None,
    ) -> MessageModel:
        msg = MessageModel(
            chat_id=chat_id,
            role=role,
            content=content,
            sources=sources,
        )
        return await self.store.pg.add_one(msg)

    async def get_messages(
        self,
        chat_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> list[MessageModel]:
        stmt = (
            select(MessageModel)
            .where(MessageModel.chat_id == chat_id)
            .order_by(MessageModel.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        return await self.store.pg.scalars_all(stmt)

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
    ) -> list[MessageModel]:
        stmt = (
            select(MessageModel)
            .where(MessageModel.chat_id == chat_id)
            .order_by(MessageModel.created_at.desc())
            .limit(limit)
        )
        messages = await self.store.pg.scalars_all(stmt)
        return list(reversed(messages))
