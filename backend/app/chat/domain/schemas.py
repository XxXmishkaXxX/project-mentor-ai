import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.chat.domain.enums import MessageRole
from app.chat.domain.models import Chat, Message


class ChatResponse(BaseModel):
    id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, chat: Chat) -> "ChatResponse":
        return cls(
            id=chat.id,
            title=chat.title,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
        )


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    id: uuid.UUID
    role: MessageRole
    content: str
    sources: list[dict] | None = None
    created_at: datetime

    @classmethod
    def from_model(cls, msg: Message) -> "MessageResponse":
        return cls(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            sources=msg.sources,
            created_at=msg.created_at,
        )


class MessageListResponse(BaseModel):
    messages: list[MessageResponse]
    total: int
