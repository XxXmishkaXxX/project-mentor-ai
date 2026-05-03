# BE-109: Chat API — CRUD чатов

**Приоритет**: Must have
**Этап**: 1
**US**: US-01, US-02
**Зависимости**: BE-103, BE-005
**Статус**: не начата

## Описание

REST API для создания, списка, получения и удаления чатов текущего пользователя с проверкой владельца.

## Файлы

- `backend/src/app/chat/schemas.py` — `ChatDTO`, `CreateChatDTO`
- `backend/src/app/chat/service.py` — бизнес-логика чатов
- `backend/src/app/chat/controller.py` — маршруты `/api/chats`

## Реализация

- Сервис: `create_chat(user_id)`, `get_chats(user_id)` — сортировка по `updated_at` DESC, `get_chat(chat_id, user_id)` с проверкой владельца, `delete_chat`.
- Контроллер: `GET /api/chats`, `POST /api/chats`, `GET /api/chats/{chat_id}`, `DELETE /api/chats/{chat_id}`.
- Доступ только владельцу (создателю чата).

## Критерии готовности

- CRUD работает для авторизованного пользователя
- Чужой чат → 403; несуществующий → 404
