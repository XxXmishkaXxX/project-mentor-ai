from litestar.testing import AsyncTestClient

from tests.constants import (
    DEFAULT_EMAIL,
    DEFAULT_PASSWORD,
    DEFAULT_USERNAME,
    OTHER_EMAIL,
    OTHER_USERNAME,
)
from tests.integration.conftest import create_user_in_db

REGISTER_URL = "/api/auth/register"


class TestRegister:
    async def test_success(self, client: AsyncTestClient):
        resp = await client.post(
            REGISTER_URL,
            json={
                "username": DEFAULT_USERNAME,
                "email": DEFAULT_EMAIL,
                "password": DEFAULT_PASSWORD,
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == DEFAULT_USERNAME
        assert data["email"] == DEFAULT_EMAIL
        assert data["role"] == "student"
        assert "id" in data

    async def test_duplicate_email(self, client: AsyncTestClient, user):
        resp = await client.post(
            REGISTER_URL,
            json={
                "username": OTHER_USERNAME,
                "email": user.email,
                "password": DEFAULT_PASSWORD,
            },
        )
        assert resp.status_code == 409

    async def test_duplicate_username(self, client: AsyncTestClient, user):
        resp = await client.post(
            REGISTER_URL,
            json={
                "username": user.username,
                "email": OTHER_EMAIL,
                "password": DEFAULT_PASSWORD,
            },
        )
        assert resp.status_code == 409

    async def test_short_password(self, client: AsyncTestClient):
        resp = await client.post(
            REGISTER_URL,
            json={
                "username": DEFAULT_USERNAME,
                "email": DEFAULT_EMAIL,
                "password": "short",
            },
        )
        assert resp.status_code == 400

    async def test_invalid_email(self, client: AsyncTestClient):
        resp = await client.post(
            REGISTER_URL,
            json={
                "username": DEFAULT_USERNAME,
                "email": "not-an-email",
                "password": DEFAULT_PASSWORD,
            },
        )
        assert resp.status_code == 400

    async def test_short_username(self, client: AsyncTestClient):
        resp = await client.post(
            REGISTER_URL,
            json={
                "username": "ab",
                "email": DEFAULT_EMAIL,
                "password": DEFAULT_PASSWORD,
            },
        )
        assert resp.status_code == 400
