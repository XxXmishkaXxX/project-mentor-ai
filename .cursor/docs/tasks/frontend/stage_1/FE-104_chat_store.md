# FE-104: Chat Store (Pinia)

**Приоритет**: Must have
**Этап**: 1
**US**: US-02
**Зависимости**: BE-109, BE-110
**Статус**: не начата

## Описание

Состояние чатов и сообщений: список чатов, текущий чат, сообщения, флаг потокового ответа. CRUD чатов и загрузка/отправка сообщений через API, включая SSE для ответа ассистента.

## Файлы

- `frontend/src/stores/chat.js` — Pinia: чаты, сообщения, стриминг
- `frontend/src/api/chat.js` — REST и SSE для чатов и сообщений

## Реализация

**State:** `chats` (array), `currentChatId` (string | null), `messages` (array), `isStreaming` (boolean).

**Actions:**

- `fetchChats()` — GET `/api/chats`
- `createChat()` — POST `/api/chats`
- `deleteChat(id)` — DELETE `/api/chats/{id}`
- `selectChat(id)` — установить `currentChatId`, подгрузить сообщения
- `fetchMessages(chatId)` — GET `/api/chats/{id}/messages` (или GET `/api/chats/{id}` по контракту)
- `sendMessage(chatId, content)` — POST `/api/chats/{id}/messages` с SSE (см. FE-112)

**api/chat.js:** `GET /api/chats`, `POST /api/chats`, `GET /api/chats/{id}`, `DELETE /api/chats/{id}`, `GET /api/chats/{id}/messages`, `POST /api/chats/{id}/messages` (SSE).

## Критерии готовности

- Чаты загружаются, создаются и удаляются
- Сообщения отправляются, ответ ассистента приходит в потоке (интеграция с FE-112)
