import secrets

import bcrypt

from app.auth.domain.schemas import LoginRequest, LoginResponse, RegisterRequest
from app.auth.exceptions import InvalidCredentialsError
from app.base.manager import BaseManager
from app.users.domain.schemas import UserResponse
from app.users.exceptions import UserAlreadyExistsError


class AuthManager(BaseManager):
    # Pre-computed hash for timing-attack mitigation: when the
    # requested email does not exist we still run bcrypt.checkpw
    # against this dummy so the response time stays constant.
    _DUMMY_HASH: str = bcrypt.hashpw(b"dummy", bcrypt.gensalt()).decode()

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
        if user is None:
            raise UserAlreadyExistsError()
        return UserResponse.from_model(user)

    async def login(self, data: LoginRequest) -> LoginResponse:
        email = str(data.email).lower().strip()
        user = await self.store.user_accessor.get_by_email(email)
        password_hash = user.password_hash if user else self._DUMMY_HASH
        valid = self.verify_password(data.password, password_hash)
        if user is None or not valid:
            raise InvalidCredentialsError()

        session_id = secrets.token_urlsafe(32)
        await self.store.session_accessor.create_session(session_id, user)
        return LoginResponse(
            session_id=session_id,
            user=UserResponse.from_model(user),
        )

    async def logout(self, session_id: str) -> None:
        await self.store.session_accessor.delete_session(session_id)
