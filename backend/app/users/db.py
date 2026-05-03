from sqlalchemy.orm import Mapped, mapped_column

from app.store.pg import models


class UserModel(models.Base, models.TimestampMixin):
    __tablename__ = "users"

    id: Mapped[models.uuid_pk]
    username: Mapped[models.str_50] = mapped_column(unique=True)
    email: Mapped[models.str_255] = mapped_column(unique=True)
    password_hash: Mapped[models.str_255]
    role: Mapped[models.str_20] = mapped_column(server_default="student")
