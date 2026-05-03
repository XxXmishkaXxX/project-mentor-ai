import uuid

from pydantic import BaseModel

from app.users.domain.enums import UserRole


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    role: UserRole
