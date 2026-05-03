# BE-102: Auth — логин и сессии

**Приоритет**: Must have
**Этап**: 1
**US**: US-01
**Зависимости**: BE-101
**Статус**: выполнена

## Описание

Реализовать вход по email и паролю: проверка пароля, создание сессии в Redis, выдача cookie клиенту.

## Файлы

- `backend/src/app/auth/schemas.py` — `LoginDTO`
- `backend/src/app/auth/service.py` — `verify_password`, `create_session`
- `backend/src/app/auth/controller.py` — endpoint `POST /api/auth/login`

## Реализация

- `LoginDTO`: `email` str, `password` str.
- Сервис: `verify_password` через `bcrypt.checkpw`.
- `create_session`: сгенерировать `session_id` (`secrets.token_urlsafe(32)`), `SET` в Redis с TTL `SESSION_TTL_HOURS * 3600`, payload JSON `{user_id, role, created_at}`.
- Контроллер: после успешной проверки — `Set-Cookie` (`HttpOnly`, `SameSite=Lax`, `Path=/`).

## Критерии готовности

- При верном email+password в заголовке ответа есть `Set-Cookie` с session_id; запись в Redis с TTL 24h (или значением из конфига)
- Неверный пароль → 401
