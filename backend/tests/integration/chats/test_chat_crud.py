import uuid

from litestar.testing import AsyncTestClient

from app.chat.db import ChatModel
from app.users.db import UserModel
from tests.constants import OTHER_EMAIL, OTHER_PASSWORD
from tests.integration.conftest import login_user

CHATS_URL = "/api/chats/"


class TestCreateChat:
    async def test_success(self, authorized_client: AsyncTestClient):
        resp = await authorized_client.post(CHATS_URL)
        assert resp.status_code == 201

        data = resp.json()
        assert "id" in data
        assert data["title"] is None
        assert "created_at" in data
        assert "updated_at" in data

    async def test_unauthorized(self, client: AsyncTestClient):
        resp = await client.post(CHATS_URL)
        assert resp.status_code == 401


class TestListChats:
    async def test_empty(self, authorized_client: AsyncTestClient):
        resp = await authorized_client.get(CHATS_URL)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_returns_own_chats(
        self,
        authorized_client: AsyncTestClient,
        chat: ChatModel,
    ):
        resp = await authorized_client.get(CHATS_URL)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == str(chat.id)

    async def test_does_not_return_other_users_chats(
        self,
        client: AsyncTestClient,
        chat: ChatModel,
        other_user: UserModel,
    ):
        session_id = await login_user(
            client,
            OTHER_EMAIL,
            OTHER_PASSWORD,
        )
        client.cookies.set("session_id", session_id)
        resp = await client.get(CHATS_URL)
        assert resp.status_code == 200
        assert resp.json() == []
        client.cookies.clear()

    async def test_unauthorized(self, client: AsyncTestClient):
        resp = await client.get(CHATS_URL)
        assert resp.status_code == 401


class TestGetChat:
    async def test_success(
        self,
        authorized_client: AsyncTestClient,
        chat: ChatModel,
    ):
        resp = await authorized_client.get(f"{CHATS_URL}{chat.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == str(chat.id)

    async def test_not_found(self, authorized_client: AsyncTestClient):
        fake_id = uuid.uuid4()
        resp = await authorized_client.get(f"{CHATS_URL}{fake_id}")
        assert resp.status_code == 404

    async def test_access_denied(
        self,
        client: AsyncTestClient,
        chat: ChatModel,
        other_user: UserModel,
    ):
        session_id = await login_user(
            client,
            OTHER_EMAIL,
            OTHER_PASSWORD,
        )
        client.cookies.set("session_id", session_id)
        resp = await client.get(f"{CHATS_URL}{chat.id}")
        assert resp.status_code == 404
        client.cookies.clear()


class TestDeleteChat:
    async def test_success(
        self,
        authorized_client: AsyncTestClient,
        chat: ChatModel,
    ):
        resp = await authorized_client.delete(f"{CHATS_URL}{chat.id}")
        assert resp.status_code == 204

        get_resp = await authorized_client.get(f"{CHATS_URL}{chat.id}")
        assert get_resp.status_code == 404

    async def test_not_found(self, authorized_client: AsyncTestClient):
        fake_id = uuid.uuid4()
        resp = await authorized_client.delete(f"{CHATS_URL}{fake_id}")
        assert resp.status_code == 404

    async def test_access_denied(
        self,
        client: AsyncTestClient,
        chat: ChatModel,
        other_user: UserModel,
    ):
        session_id = await login_user(
            client,
            OTHER_EMAIL,
            OTHER_PASSWORD,
        )
        client.cookies.set("session_id", session_id)
        resp = await client.delete(f"{CHATS_URL}{chat.id}")
        assert resp.status_code == 404
        client.cookies.clear()
