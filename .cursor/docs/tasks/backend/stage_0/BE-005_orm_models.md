# BE-005: ORM-модели

**Приоритет**: Блокирующий
**Этап**: 0
**US**: -
**Зависимости**: BE-004
**Статус**: не начата

## Описание

Описать доменные сущности User, Chat, Message, Feedback, Document в стиле SQLAlchemy 2.0 declarative.

## Файлы

- `backend/src/app/db/models.py` — все ORM-модели, связи, ограничения, индексы

## Реализация

- Стиль SQLAlchemy 2.0: `Mapped`, `mapped_column`.
- **User**: `id` UUID PK, `username` VARCHAR(50) UNIQUE, `email` VARCHAR(255) UNIQUE, `password_hash` VARCHAR(255), `role` VARCHAR(20) default `'student'`, `created_at` / `updated_at` TIMESTAMPTZ.
- **Chat**: `id` UUID PK, `user_id` FK → users ON DELETE CASCADE, `title` VARCHAR(255), timestamps.
- **Message**: `id` UUID PK, `chat_id` FK → chats CASCADE, `role` VARCHAR(20), `content` TEXT, `sources` JSONB nullable, `created_at`.
- **Feedback**: `id` UUID PK, `message_id` FK messages CASCADE, `user_id` FK users CASCADE, `is_helpful` BOOLEAN, `comment` TEXT nullable, `created_at`; `UniqueConstraint(message_id, user_id)`.
- **Document**: `id` UUID PK, `filename`, `title`, `description` nullable, `status` default `'pending'`, `error_message` nullable, `file_path`, `chunk_count` default 0, `uploaded_by` FK users nullable, timestamps.
- Индексы: `user_id` в chats, `chat_id` в messages.

## Критерии готовности

- Миграция создаёт все 5 таблиц с корректными колонками, FK и индексами
- Ограничение уникальности feedback по паре (message_id, user_id) применяется в БД
