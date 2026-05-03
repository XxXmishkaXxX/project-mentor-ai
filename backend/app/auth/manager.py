import secrets

import bcrypt

from app.auth.domain.schemas import LoginRequest, RegisterRequest
from app.auth.exceptions import InvalidCredentialsError
from app.base.manager import BaseManager
from app.users.domain.schemas import UserResponse

_DUMMY_HASH = bcrypt.hashpw(b"dummy", bcrypt.gensalt()).decode()


class AuthManager(BaseManager):
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt(),
        ).decode()

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(
                password.encode(),
                password_hash.encode(),
            )
        except (ValueError, TypeError):
            return False

    async def register(self, data: RegisterRequest) -> UserResponse:
        password_hash = self.hash_password(data.password)
        user = await self.store.user_accessor.create_user(
            username=data.username,
            email=str(data.email).lower().strip(),
            password_hash=password_hash,
        )
        return self.store.user_manager.to_response(user)

    async def login(
        self,
        data: LoginRequest,
    ) -> tuple[str, UserResponse]:
        email = str(data.email).lower().strip()
        user = await self.store.user_accessor.get_by_email(email)
        password_hash = user.password_hash if user else _DUMMY_HASH
        valid = self.verify_password(data.password, password_hash)
        if user is None or not valid:
            raise InvalidCredentialsError()

        session_id = secrets.token_urlsafe(32)
        await self.store.session_accessor.create_session(session_id, user)
        return session_id, self.store.user_manager.to_response(user)

    async def logout(self, session_id: str) -> None:
        await self.store.session_accessor.delete_session(session_id)
