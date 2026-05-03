import uuid
from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.common.config import StaticConfig

DATETIME_DEFAULT = text("CURRENT_TIMESTAMP")

uuid_pk = Annotated[
    uuid.UUID,
    mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    ),
]

str_20 = Annotated[str, mapped_column(String(StaticConfig.SQL_STR_LEN_SMALL))]
str_50 = Annotated[
    str,
    mapped_column(String(StaticConfig.SQL_STR_LEN_MEDIUM)),
]
str_100 = Annotated[
    str,
    mapped_column(String(StaticConfig.SQL_STR_LEN_LARGE)),
]
str_255 = Annotated[
    str,
    mapped_column(String(StaticConfig.SQL_STR_LEN_XLARGE)),
]
str_500 = Annotated[
    str,
    mapped_column(String(StaticConfig.SQL_STR_LEN_TEXT)),
]

DateTimeField = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now()),
]

AutoUpdatedField = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    ),
]


class TimestampMixin:
    created_at: Mapped[DateTimeField]
    updated_at: Mapped[AutoUpdatedField]


class Base(DeclarativeBase):
    pass
