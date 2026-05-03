# US-10: Оценка качества ответа

**Приоритет**: Should have
**Итерация**: 2
**Модуль**: feedback
**Backend**: `backend/src/app/feedback/controller.py` — POST `/api/messages/{message_id}/feedback`
**Frontend**: `FeedbackButtons.vue`

## Формулировка

Как студент, я хочу оценить ответ ассистента на сайте, чтобы помочь команде улучшать качество системы.

## Критерии приёмки

- под ответом есть кнопки оценки: «полезно» и «не полезно»
- пользователь может оставить короткий комментарий
- оценка сохраняется в системе
- разработчик может посмотреть собранные оценки
- обратная связь используется для улучшения базы знаний и поиска

## Технические детали

POST `/api/messages/{id}/feedback` с телом `{is_helpful, comment}`. UNIQUE(`message_id`, `user_id`). FeedbackButtons: thumbs up/down + optional comment modal.
