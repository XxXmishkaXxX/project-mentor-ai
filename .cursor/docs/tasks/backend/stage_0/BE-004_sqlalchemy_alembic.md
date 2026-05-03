# BE-004: SQLAlchemy + Alembic

**Приоритет**: Блокирующий
**Этап**: 0
**US**: -
**Зависимости**: BE-003
**Статус**: не начата

## Описание

Настроить асинхронный движок SQLAlchemy, фабрику сессий и Alembic для миграций схемы БД.

## Файлы

- `backend/src/app/db/base.py` — `DeclarativeBase`, фабрика engine/session
- `backend/migrations/env.py` — окружение Alembic для async и autogenerate
- `backend/migrations/script.py.mako` — шаблон ревизий
- `backend/alembic.ini` — пути к миграциям и логирование

## Реализация

- `create_async_engine` с драйвером `asyncpg`, `async_sessionmaker`.
- В `env.py` Alembic — async-режим, `run_migrations_online` с connectable для async.
- Импорт моделей в `env.py` для корректного autogenerate.

## Критерии готовности

- `alembic revision --autogenerate` создаёт миграции на основе моделей
- `alembic upgrade head` применяет миграции к PostgreSQL
