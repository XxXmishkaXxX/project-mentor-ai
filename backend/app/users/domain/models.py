import uuid

from pydantic import BaseModel

from app.users.domain.enums import UserRole


class User(BaseModel):
    """Internal user model for business logic."""

    id: uuid.UUID
    username: str
    email: str
    role: UserRole
    password_hash: str
