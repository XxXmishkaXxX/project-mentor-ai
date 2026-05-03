import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    id: uuid.UUID
    role: Literal["user", "assistant", "system"]
    content: str
    sources: list[dict] | None = None
    created_at: datetime


class MessageListResponse(BaseModel):
    messages: list[MessageResponse]
    total: int
