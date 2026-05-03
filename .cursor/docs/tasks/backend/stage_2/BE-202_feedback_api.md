# BE-202: Feedback API

**Приоритет**: Should have
**Этап**: 2
**US**: US-10
**Зависимости**: BE-005, BE-103
**Статус**: не начата

## Описание

`POST /api/messages/{message_id}/feedback` — сохранение оценки полезности ответа ассистента с опциональным комментарием.

## Файлы

- `backend/src/app/feedback/schemas.py` — `FeedbackDTO`
- `backend/src/app/feedback/service.py` — валидация сообщения и сохранение feedback
- `backend/src/app/feedback/controller.py` — HTTP endpoint

## Реализация

- `FeedbackDTO`: `is_helpful` bool, `comment` str optional.
- Сервис: проверка существования сообщения и `role == assistant`; проверка уникальности пары (message_id, user_id); INSERT.
- Контроллер: `POST /api/messages/{message_id}/feedback`, ответ 201.

## Критерии готовности

- Feedback сохраняется для assistant-сообщения
- Повтор от того же пользователя на то же сообщение → 409
- Для user-сообщений feedback не принимается (4xx по спецификации проекта)
