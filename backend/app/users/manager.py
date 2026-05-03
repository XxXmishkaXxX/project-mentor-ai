import uuid

from app.base.manager import BaseManager
from app.users.domain.schemas import UserResponse
from app.users.exceptions import UserNotFoundError


class UserManager(BaseManager):
    def to_response(self, user) -> UserResponse:  # noqa: ANN001
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
        )

    async def get_current_user(
        self,
        user_id: uuid.UUID,
    ) -> UserResponse:
        user = await self.store.user_accessor.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()
        return self.to_response(user)
