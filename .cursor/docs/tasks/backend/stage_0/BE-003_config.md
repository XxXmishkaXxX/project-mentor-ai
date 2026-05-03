# BE-003: Конфигурация приложения

**Приоритет**: Блокирующий
**Этап**: 0
**US**: -
**Зависимости**: BE-001
**Статус**: не начата

## Описание

Централизованное чтение настроек из переменных окружения и `.env` через Pydantic Settings для использования в Litestar и сервисах.

## Файлы

- `backend/src/app/config.py` — класс `Settings`, URL БД, singleton `get_settings()`

## Реализация

- Класс `Settings(BaseSettings)` с `model_config` для чтения `.env`.
- Поля: `PG_HOST`, `PG_PORT`, `PG_DB`, `PG_USER`, `PG_PASSWORD`, `REDIS_HOST`, `REDIS_PORT`, `QDRANT_HOST`, `QDRANT_PORT`, `QWEN_API_KEY`, `QWEN_API_BASE_URL`, `QWEN_MODEL`, `QWEN_EMBEDDING_MODEL`, `SECRET_KEY`, `SESSION_TTL_HOURS`, `CORS_ORIGINS`, `RAG_TOP_K`, `RAG_SCORE_THRESHOLD`, `RAG_CHUNK_SIZE`, `RAG_CHUNK_OVERLAP`.
- Property `database_url` для async SQLAlchemy (asyncpg).
- Экземпляр настроек через `get_settings()` (singleton / lru_cache) для dependency injection в Litestar.

## Критерии готовности

- `Settings` корректно подхватывает значения из `.env`
- Настройки доступны как dependency в Litestar handlers / сервисах
