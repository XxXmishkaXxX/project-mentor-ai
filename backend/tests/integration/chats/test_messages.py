from litestar.testing import AsyncTestClient

from app.chat.db import ChatModel
from app.store.store import Store


class TestGetMessages:
    async def test_empty(
        self,
        authorized_client: AsyncTestClient,
        chat: ChatModel,
    ):
        resp = await authorized_client.get(
            f"/api/chats/{chat.id}/messages",
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["messages"] == []
        assert data["total"] == 0

    async def test_returns_messages(
        self,
        authorized_client: AsyncTestClient,
        chat: ChatModel,
        store: Store,
    ):
        await store.chat_accessor.add_message(
            chat_id=chat.id,
            role="user",
            content="Hello!",
        )
        await store.chat_accessor.add_message(
            chat_id=chat.id,
            role="assistant",
            content="Hi there!",
        )

        resp = await authorized_client.get(
            f"/api/chats/{chat.id}/messages",
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["messages"]) == 2
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][0]["content"] == "Hello!"
        assert data["messages"][1]["role"] == "assistant"

    async def test_pagination(
        self,
        authorized_client: AsyncTestClient,
        chat: ChatModel,
        store: Store,
    ):
        for i in range(5):
            await store.chat_accessor.add_message(
                chat_id=chat.id,
                role="user",
                content=f"Message {i}",
            )

        resp = await authorized_client.get(
            f"/api/chats/{chat.id}/messages",
            params={"offset": 0, "limit": 2},
        )
        data = resp.json()
        assert data["total"] == 5
        assert len(data["messages"]) == 2
        assert data["messages"][0]["content"] == "Message 0"

        resp2 = await authorized_client.get(
            f"/api/chats/{chat.id}/messages",
            params={"offset": 2, "limit": 2},
        )
        data2 = resp2.json()
        assert len(data2["messages"]) == 2
        assert data2["messages"][0]["content"] == "Message 2"

    async def test_unauthorized(
        self,
        client: AsyncTestClient,
        chat: ChatModel,
    ):
        resp = await client.get(f"/api/chats/{chat.id}/messages")
        assert resp.status_code == 401
