import secrets

import bcrypt

from app.auth.domain.schemas import LoginRequest, RegisterRequest
from app.auth.exceptions import InvalidCredentialsError
from app.base.manager import BaseManager
from app.users.domain.schemas import UserResponse


class AuthManager(BaseManager):
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt(),
        ).decode()

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(
            password.encode(),
            password_hash.encode(),
        )

    async def register(self, data: RegisterRequest) -> UserResponse:
        password_hash = self.hash_password(data.password)
        user = await self.store.user_accessor.create_user(
            username=data.username,
            email=data.email,
            password_hash=password_hash,
        )
        return self.store.user_manager.to_response(user)

    async def login(
        self,
        data: LoginRequest,
    ) -> tuple[str, UserResponse]:
        user = await self.store.user_accessor.get_by_email(data.email)
        if user is None or not self.verify_password(
            data.password,
            user.password_hash,
        ):
            raise InvalidCredentialsError()

        session_id = secrets.token_urlsafe(32)
        await self.store.session_accessor.create_session(session_id, user)
        return session_id, self.store.user_manager.to_response(user)

    async def logout(self, session_id: str) -> None:
        await self.store.session_accessor.delete_session(session_id)
