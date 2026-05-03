import uuid

from pydantic import BaseModel

from app.users.db import UserModel
from app.users.domain.enums import UserRole


class User(BaseModel):
    """Internal user model for business logic."""

    id: uuid.UUID
    username: str
    email: str
    role: UserRole
    password_hash: str

    @classmethod
    def from_db(cls, db: UserModel) -> "User":
        return cls(
            id=db.id,
            username=db.username,
            email=db.email,
            role=UserRole(db.role),
            password_hash=db.password_hash,
        )
