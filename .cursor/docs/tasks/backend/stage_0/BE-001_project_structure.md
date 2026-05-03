# BE-001: Структура проекта и зависимости

**Приоритет**: Блокирующий
**Этап**: 0
**US**: -
**Зависимости**: -
**Статус**: не начата

## Описание

Создать структуру каталогов backend, настроить pyproject.toml / requirements.txt для управления зависимостями и точкой входа приложения.

## Файлы

- `backend/pyproject.toml` — конфигурация проекта и зависимостей (или метаданные пакета)
- `backend/requirements.txt` — фиксированные версии зависимостей для развёртывания
- `backend/src/app/__init__.py` — пакет приложения
- `backend/src/app/main.py` — заглушка приложения Litestar с минимальным API

## Реализация

- Зависимости: litestar, uvicorn, sqlalchemy[asyncio], asyncpg, alembic, redis[hiredis], qdrant-client, httpx, pydantic, pydantic-settings, bcrypt, python-multipart, pypdf2, python-docx.
- Структура каталогов согласно документу architecture (src-layout, модули app).
- В `main.py` — минимальное приложение Litestar и маршрут `GET /api/health` (можно заглушка 200 до BE-113).

## Критерии готовности

- `uvicorn backend.src.app.main:app` запускается без ошибок
- `GET /api/health` возвращает HTTP 200
