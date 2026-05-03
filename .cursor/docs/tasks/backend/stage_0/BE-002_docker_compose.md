# BE-002: Docker Compose

**Приоритет**: Блокирующий
**Этап**: 0
**US**: -
**Зависимости**: -
**Статус**: не начата

## Описание

Поднять локальную инфраструктуру: PostgreSQL 16, Qdrant, Redis 7 через Docker Compose с именованными томами и примером переменных окружения.

## Файлы

- `docker-compose.yml` — описание сервисов postgres, qdrant, redis
- `.env.example` — шаблон переменных (PG, Redis, Qdrant, Qwen API, App, RAG)

## Реализация

- Три сервиса: `postgres:16-alpine`, `qdrant/qdrant:latest`, `redis:7-alpine`.
- Порты: 5432 (Postgres), 6333/6334 (Qdrant), 6379 (Redis).
- Именованные тома: `pg_data`, `qdrant_data`.
- Подстановка из env для пароля БД и прочих секретов (`PG_PASSWORD` и др.).
- `.env.example` включает все переменные: PostgreSQL, Redis, Qdrant, Qwen API, приложение, настройки RAG.

## Критерии готовности

- `docker compose up -d` успешно поднимает все три сервиса
- Сервисы доступны на localhost с указанными портами
