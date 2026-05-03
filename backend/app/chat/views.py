import uuid

from litestar import delete, get, post
from litestar.params import Parameter
from litestar.response import Stream

from app.base.view import BaseView
from app.chat.domain.schemas import (
    ChatResponse,
    MessageListResponse,
    SendMessageRequest,
)
from app.web.request import AppRequest


class ChatView(BaseView):
    path = "/api/chats"

    @get("/")
    async def list_chats(self, request: AppRequest) -> list[ChatResponse]:
        return await self.store.chat_manager.get_chats(
            request.user.user_id,
        )

    @post("/", status_code=201)
    async def create_chat(self, request: AppRequest) -> ChatResponse:
        return await self.store.chat_manager.create_chat(
            request.user.user_id,
        )

    @get("/{chat_id:uuid}")
    async def get_chat(
        self,
        request: AppRequest,
        chat_id: uuid.UUID,
    ) -> ChatResponse:
        return await self.store.chat_manager.get_chat(
            chat_id,
            request.user.user_id,
        )

    @delete("/{chat_id:uuid}", status_code=204)
    async def delete_chat(
        self,
        request: AppRequest,
        chat_id: uuid.UUID,
    ) -> None:
        await self.store.chat_manager.delete_chat(
            chat_id,
            request.user.user_id,
        )

    @get("/{chat_id:uuid}/messages")
    async def get_messages(
        self,
        request: AppRequest,
        chat_id: uuid.UUID,
        offset: int = Parameter(default=0, ge=0),
        limit: int = Parameter(default=50, ge=1, le=100),
    ) -> MessageListResponse:
        return await self.store.chat_manager.get_messages(
            chat_id,
            request.user.user_id,
            offset=offset,
            limit=limit,
        )

    @post("/{chat_id:uuid}/messages")
    async def send_message(
        self,
        request: AppRequest,
        chat_id: uuid.UUID,
        data: SendMessageRequest,
    ) -> Stream:
        return Stream(
            self.store.chat_manager.send_message(
                chat_id,
                request.user.user_id,
                data.content,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )
