import uuid

from pydantic import BaseModel

from app.users.domain.enums import UserRole
from app.users.domain.models import User


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    role: UserRole

    @classmethod
    def from_model(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
        )
