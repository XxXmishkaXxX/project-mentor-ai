import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.auth.domain.schemas import LoginRequest, RegisterRequest
from app.auth.exceptions import InvalidCredentialsError
from app.auth.manager import AuthManager


class TestHashPassword:
    def test_returns_different_from_input(self):
        hashed = AuthManager.hash_password("password123")
        assert hashed != "password123"
        assert len(hashed) > 0

    def test_different_calls_produce_different_hashes(self):
        h1 = AuthManager.hash_password("password123")
        h2 = AuthManager.hash_password("password123")
        assert h1 != h2


class TestVerifyPassword:
    def test_correct_password(self):
        hashed = AuthManager.hash_password("mypassword")
        assert AuthManager.verify_password("mypassword", hashed) is True

    def test_wrong_password(self):
        hashed = AuthManager.hash_password("mypassword")
        assert AuthManager.verify_password("wrong", hashed) is False


class TestRegister:
    async def test_creates_user_and_returns_response(
        self,
        auth_manager: AuthManager,
        mock_store: MagicMock,
    ):
        fake_user = MagicMock()
        fake_user.id = uuid.uuid4()
        fake_user.username = "newuser"
        fake_user.email = "new@example.com"
        fake_user.role = "student"

        mock_store.user_accessor.create_user = AsyncMock(
            return_value=fake_user,
        )

        data = RegisterRequest(
            username="newuser",
            email="new@example.com",
            password="securepass123",
        )
        result = await auth_manager.register(data)

        mock_store.user_accessor.create_user.assert_called_once()
        call_kwargs = mock_store.user_accessor.create_user.call_args.kwargs
        assert call_kwargs["username"] == "newuser"
        assert call_kwargs["email"] == "new@example.com"
        assert call_kwargs["password_hash"] != "securepass123"

        assert result.username == "newuser"
        assert result.email == "new@example.com"


class TestLogin:
    async def test_success(
        self,
        auth_manager: AuthManager,
        mock_store: MagicMock,
    ):
        password = "correctpassword"
        password_hash = AuthManager.hash_password(password)

        fake_user = MagicMock()
        fake_user.id = uuid.uuid4()
        fake_user.username = "loginuser"
        fake_user.email = "login@example.com"
        fake_user.password_hash = password_hash
        fake_user.role = "student"

        mock_store.user_accessor.get_by_email = AsyncMock(
            return_value=fake_user,
        )
        mock_store.session_accessor.create_session = AsyncMock()

        data = LoginRequest(email="login@example.com", password=password)
        result = await auth_manager.login(data)

        assert len(result.session_id) > 0
        assert result.user.email == "login@example.com"
        mock_store.session_accessor.create_session.assert_called_once()

    async def test_user_not_found(
        self,
        auth_manager: AuthManager,
        mock_store: MagicMock,
    ):
        mock_store.user_accessor.get_by_email = AsyncMock(return_value=None)

        data = LoginRequest(email="noone@example.com", password="whatever")
        with pytest.raises(InvalidCredentialsError):
            await auth_manager.login(data)

    async def test_wrong_password(
        self,
        auth_manager: AuthManager,
        mock_store: MagicMock,
    ):
        fake_user = MagicMock()
        fake_user.password_hash = AuthManager.hash_password("realpassword")

        mock_store.user_accessor.get_by_email = AsyncMock(
            return_value=fake_user,
        )

        data = LoginRequest(email="user@example.com", password="wrongone")
        with pytest.raises(InvalidCredentialsError):
            await auth_manager.login(data)


class TestLogout:
    async def test_calls_delete_session(
        self,
        auth_manager: AuthManager,
        mock_store: MagicMock,
    ):
        mock_store.session_accessor.delete_session = AsyncMock()

        await auth_manager.logout("some-session-id")

        mock_store.session_accessor.delete_session.assert_called_once_with(
            "some-session-id",
        )
