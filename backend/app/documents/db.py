import uuid

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.store.pg import models


class DocumentModel(models.Base, models.TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[models.uuid_pk]
    filename: Mapped[models.str_255]
    title: Mapped[models.str_255]
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[models.str_20] = mapped_column(
        server_default="pending",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    file_path: Mapped[models.str_500]
    chunk_count: Mapped[int] = mapped_column(
        default=0,
        server_default="0",
    )
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
