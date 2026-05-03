import uuid
from datetime import datetime

from pydantic import BaseModel

from app.chat.db import ChatModel, MessageModel
from app.chat.domain.enums import MessageRole


class Chat(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_db(cls, db: ChatModel) -> "Chat":
        return cls(
            id=db.id,
            user_id=db.user_id,
            title=db.title,
            created_at=db.created_at,
            updated_at=db.updated_at,
        )


class Message(BaseModel):
    id: uuid.UUID
    chat_id: uuid.UUID
    role: MessageRole
    content: str
    sources: list[dict] | None = None
    created_at: datetime

    @classmethod
    def from_db(cls, db: MessageModel) -> "Message":
        return cls(
            id=db.id,
            chat_id=db.chat_id,
            role=MessageRole(db.role),
            content=db.content,
            sources=db.sources,
            created_at=db.created_at,
        )


class ChatMessage(BaseModel):
    """A single message in the LLM conversation context."""

    role: MessageRole
    content: str
