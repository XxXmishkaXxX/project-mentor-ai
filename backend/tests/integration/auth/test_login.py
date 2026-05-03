from litestar.testing import AsyncTestClient

from app.users.db import UserModel
from tests.constants import DEFAULT_EMAIL, DEFAULT_PASSWORD

LOGIN_URL = "/api/auth/login"


class TestLogin:
    async def test_success(
        self,
        client: AsyncTestClient,
        registered_user: UserModel,
    ):
        resp = await client.post(
            LOGIN_URL,
            json={
                "email": DEFAULT_EMAIL,
                "password": DEFAULT_PASSWORD,
            },
        )
        assert resp.status_code == 201

        data = resp.json()
        assert data["email"] == DEFAULT_EMAIL
        assert data["username"] == registered_user.username
        assert data["role"] == "student"

        assert "session_id" in resp.cookies

    async def test_wrong_password(
        self,
        client: AsyncTestClient,
        registered_user: UserModel,
    ):
        resp = await client.post(
            LOGIN_URL,
            json={
                "email": DEFAULT_EMAIL,
                "password": "wrong-password",
            },
        )
        assert resp.status_code == 401

    async def test_nonexistent_email(self, client: AsyncTestClient):
        resp = await client.post(
            LOGIN_URL,
            json={
                "email": "noone@example.com",
                "password": DEFAULT_PASSWORD,
            },
        )
        assert resp.status_code == 401

    async def test_session_cookie_works(
        self,
        client: AsyncTestClient,
        registered_user: UserModel,
    ):
        resp = await client.post(
            LOGIN_URL,
            json={
                "email": DEFAULT_EMAIL,
                "password": DEFAULT_PASSWORD,
            },
        )
        assert resp.status_code == 201
        session_id = resp.cookies.get("session_id")
        assert session_id

        client.cookies.set("session_id", session_id)
        me_resp = await client.get("/api/users/me")
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == DEFAULT_EMAIL
        client.cookies.clear()


class TestLogout:
    async def test_success(
        self,
        client: AsyncTestClient,
        registered_user: UserModel,
    ):
        login_resp = await client.post(
            LOGIN_URL,
            json={
                "email": DEFAULT_EMAIL,
                "password": DEFAULT_PASSWORD,
            },
        )
        assert login_resp.status_code == 201
        session_id = login_resp.cookies.get("session_id")
        client.cookies.set("session_id", session_id)

        logout_resp = await client.post("/api/auth/logout")
        assert logout_resp.status_code == 201

        me_resp = await client.get("/api/users/me")
        assert me_resp.status_code == 401
        client.cookies.clear()

    async def test_unauthorized(self, client: AsyncTestClient):
        resp = await client.post("/api/auth/logout")
        assert resp.status_code == 401
