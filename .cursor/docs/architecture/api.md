# API эндпоинты

Все эндпоинты имеют префикс `/api`. Авторизация через cookie `session_id`.

## Auth

| Метод | Путь | Описание | Auth | Request Body | Response |
|-------|------|----------|------|--------------|----------|
| POST | /api/auth/register | Регистрация | - | `{username, email, password}` | `{id, username, email, role}` 201 |
| POST | /api/auth/login | Вход | - | `{email, password}` | `{id, username, email, role}` + Set-Cookie |
| POST | /api/auth/logout | Выход | required | - | 204 |
| GET | /api/auth/me | Текущий пользователь | required | - | `{id, username, email, role}` |

Ошибки: 401 (неверный пароль), 409 (дубликат email/username), 422 (валидация)

## Chats

| Метод | Путь | Описание | Auth | Response |
|-------|------|----------|------|----------|
| GET | /api/chats | Список чатов | required | `[{id, title, created_at, updated_at}]` |
| POST | /api/chats | Создать чат | required | `{id, title, created_at}` 201 |
| GET | /api/chats/{chat_id} | Чат с сообщениями | required | `{id, title, messages: [...]}` |
| DELETE | /api/chats/{chat_id} | Удалить чат | required | 204 |

Ошибки: 403 (чужой чат), 404 (не найден)

## Messages

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | /api/chats/{chat_id}/messages | История сообщений | required |
| POST | /api/chats/{chat_id}/messages | Отправить вопрос (SSE) | required |

GET: `[{id, role, content, sources, created_at}]` (пагинация: ?offset=0&limit=50)

POST body: `{content: "Как составить ТЗ?"}`

POST response: `text/event-stream`

### SSE формат

```
event: token
data: {"text": "Sprint"}

event: token
data: {"text": " Backlog"}

event: sources
data: {"sources": [{"document_title": "...", "chunk_text": "...", "score": 0.92}]}

event: done
data: {"message_id": "uuid"}
```

## Feedback

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| POST | /api/messages/{message_id}/feedback | Оценить ответ | required |

Body: `{"is_helpful": true, "comment": "Очень помогло"}`

Response: 201

Ошибки: 409 (уже оценено этим пользователем)

## Admin

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | /api/admin/documents | Список документов | admin |
| POST | /api/admin/documents | Загрузить документ | admin |
| DELETE | /api/admin/documents/{doc_id} | Удалить + чанки | admin |
| POST | /api/admin/documents/{doc_id}/reindex | Переиндексировать | admin |

POST: multipart/form-data (file + title + description)

GET: `[{id, filename, title, status, chunk_count, created_at}]`

## Health

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | /api/health | Статус сервисов | - |

Response: `{"pg": "ok", "qdrant": "ok", "redis": "ok"}`
