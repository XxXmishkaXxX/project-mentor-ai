import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.chat.domain.enums import MessageRole
from app.common.config import StaticConfig
from app.store.pg import models

_ROLE_VALUES = tuple(r.value for r in MessageRole)


class ChatModel(models.Base, models.TimestampMixin):
    __tablename__ = "chats"

    id: Mapped[models.uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(
        String(StaticConfig.SQL_STR_LEN_XLARGE),
        nullable=True,
    )

    messages: Mapped[list["MessageModel"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
    )

    __table_args__ = (Index("idx_chats_user_id", "user_id"),)


class MessageModel(models.Base):
    __tablename__ = "messages"

    id: Mapped[models.uuid_pk]
    chat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[models.str_20]
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[models.DateTimeField]

    chat: Mapped["ChatModel"] = relationship(back_populates="messages")

    __table_args__ = (
        Index("idx_messages_chat_id", "chat_id"),
        CheckConstraint(
            f"role IN {_ROLE_VALUES!r}",
            name="ck_messages_role",
        ),
    )
