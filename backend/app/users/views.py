from litestar import get

from app.base.view import BaseView
from app.users.domain.schemas import UserResponse
from app.web.request import Request


class UserView(BaseView):
    path = "/api/users"

    @get("/me")
    async def me(self, request: Request) -> UserResponse:
        return await self.store.user_manager.get_current_user(
            request.user.user_id,
        )
