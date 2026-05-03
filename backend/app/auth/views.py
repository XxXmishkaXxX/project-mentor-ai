from litestar import Request, Response, post
from litestar.datastructures import Cookie

from app.auth.domain.schemas import LoginRequest, RegisterRequest
from app.base.view import BaseView
from app.common.config import StaticConfig
from app.users.domain.schemas import UserResponse


class AuthView(BaseView):
    path = "/api/auth"

    @post("/register", status_code=201)
    async def register(self, data: RegisterRequest) -> UserResponse:
        return await self.store.auth_manager.register(data)

    @post("/login")
    async def login(self, data: LoginRequest) -> Response[UserResponse]:
        session_id, user = await self.store.auth_manager.login(data)
        return Response(
            content=user,
            cookies=[
                Cookie(
                    key=StaticConfig.SESSION_COOKIE_NAME,
                    value=session_id,
                    httponly=True,
                    samesite="lax",
                    secure=True,
                    path="/",
                    max_age=StaticConfig.SESSION_TTL_HOURS * 3600,
                ),
            ],
        )

    @post("/logout")
    async def logout(self, request: Request) -> Response[dict]:
        session_id = request.cookies.get(StaticConfig.SESSION_COOKIE_NAME)
        if session_id:
            await self.store.auth_manager.logout(session_id)
        return Response(
            content={"detail": "Logged out"},
            cookies=[
                Cookie(
                    key=StaticConfig.SESSION_COOKIE_NAME,
                    value="",
                    httponly=True,
                    samesite="lax",
                    secure=True,
                    path="/",
                    max_age=0,
                ),
            ],
        )
