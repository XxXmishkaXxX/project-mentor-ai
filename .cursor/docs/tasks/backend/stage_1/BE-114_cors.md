# BE-114: CORS настройка

**Приоритет**: Must have
**Этап**: 1
**US**: -
**Зависимости**: BE-001
**Статус**: не начата

## Описание

Настроить CORS для фронтенда в dev (в т.ч. `http://localhost:5173`) с поддержкой учётных данных (cookies).

## Файлы

- `backend/src/app/main.py` — `CORSConfig` Litestar

## Реализация

- `allow_origins` из переменной `CORS_ORIGINS` (список через запятую или формат, принятый в проекте).
- `allow_credentials=True`.
- `allow_methods=["*"]`, `allow_headers=["*"]` (или минимально необходимый настрой в соответствии с security policy).

## Критерии готовности

- Фронт на `localhost:5173` может вызывать API
- Cookie сессии передаются в cross-origin запросах согласно настройке
