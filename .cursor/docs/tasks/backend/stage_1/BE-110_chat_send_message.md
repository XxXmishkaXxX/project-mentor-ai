# BE-110: Chat API — отправка сообщения (SSE)

**Приоритет**: Must have
**Этап**: 1
**US**: US-02, US-03, US-07, US-08
**Зависимости**: BE-108, BE-109
**Статус**: не начата

## Описание

`POST /api/chats/{chat_id}/messages` — сохранение сообщения пользователя, вызов RAG pipeline, потоковый ответ через SSE, сохранение ответа ассистента.

## Файлы

- `backend/src/app/chat/controller.py` — endpoint отсылки сообщения, `StreamingResponse`
- `backend/src/app/chat/service.py` — сохранение сообщений, вызов pipeline, обновление чата

## Реализация

- `SendMessageDTO`: `content` str.
- Сервис: 1) сохранить user message в PG; 2) загрузить историю (последние N сообщений); 3) `pipeline.ask(content, history)`; 4) стрим SSE (`token`, `sources`, `done`); 5) собрать полный текст ответа; 6) сохранить assistant message + `sources`; 7) обновить `chat.title` (первый вопрос, до 100 символов) и `chat.updated_at`.
- Контроллер: `StreamingResponse`, `media_type="text/event-stream"`.

## Критерии готовности

- SSE stream стабильно отдаёт события; сообщения пишутся в PG
- `title` чата выставляется из первого пользовательского сообщения (усечённого)
