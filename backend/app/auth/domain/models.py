import uuid
from datetime import datetime

from pydantic import BaseModel

from app.users.domain.enums import UserRole


class SessionUser(BaseModel):
    """User data stored in the Redis session."""

    user_id: uuid.UUID
    role: UserRole
    created_at: datetime
