# BE-111: Chat API — история сообщений

**Приоритет**: Must have
**Этап**: 1
**US**: US-02
**Зависимости**: BE-109
**Статус**: выполнена

## Описание

`GET /api/chats/{chat_id}/messages` — постраничная выдача истории сообщений с полями включая источники.

## Файлы

- `backend/app/chat/views.py` — query params, проверка владельца
- `backend/app/chat/manager.py` — получение и пагинация сообщений

## Реализация

- Query: `offset` (default 0), `limit` (default 50).
- Сообщения по `created_at` ASC.
- В каждом элементе: `id`, `role`, `content`, `sources`, `created_at`.
- Проверка, что `chat_id` принадлежит текущему пользователю.

## Критерии готовности

- Возвращаются сообщения с `sources`, порядок `created_at` asc
- Пагинация `offset` / `limit` работает корректно
