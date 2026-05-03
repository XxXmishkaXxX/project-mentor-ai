# BE-103: Auth — middleware, logout, me

**Приоритет**: Must have
**Этап**: 1
**US**: US-01
**Зависимости**: BE-102
**Статус**: выполнена

## Описание

Middleware сессии: извлечение cookie, проверка в Redis, помещение текущего пользователя в `request.state`. Endpoints `GET /api/auth/me` и `POST /api/auth/logout`.

## Файлы

- `backend/src/app/auth/middleware.py` — проверка сессии, whitelist путей
- `backend/src/app/auth/controller.py` — `logout`, `me`

## Реализация

- Middleware: взять `session_id` из cookie → `GET` из Redis → распарсить JSON → `request.state.user`.
- Исключения (без обязательной сессии): `/api/auth/login`, `/api/auth/register`, `/api/health`.
- `GET /api/auth/me`: вернуть текущего пользователя из `request.state`.
- `POST /api/auth/logout`: `DEL` сессии в Redis, сброс/очистка cookie.

## Критерии готовности

- Запросы без cookie к защищённым маршрутам → 401
- С валидной cookie пользователь доступен в handler
- `/logout` удаляет сессию; `/me` возвращает данные пользователя
