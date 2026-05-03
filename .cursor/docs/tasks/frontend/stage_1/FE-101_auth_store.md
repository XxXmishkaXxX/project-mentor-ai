# FE-101: Auth Store (Pinia)

**Приоритет**: Must have
**Этап**: 1
**US**: US-01
**Зависимости**: BE-101, BE-102, BE-103
**Статус**: не начата

## Описание

Центральное состояние аутентификации: текущий пользователь, флаг загрузки, вычисляемая авторизация. Действия для входа, регистрации, выхода и загрузки профиля через backend API.

## Файлы

- `frontend/src/stores/auth.js` — Pinia store: state, getters, actions
- `frontend/src/api/auth.js` — методы обращения к эндпоинтам `/api/auth/*`

## Реализация

**State:** `user` (object | null), `isLoading` (boolean).

**Getters / computed:** `isAuthenticated` — производное от `user !== null` (или от валидного токена/сессии по контракту API).

**Actions:**

- `login(email, password)` — POST `/api/auth/login`, обновить `user`
- `register(username, email, password)` — POST `/api/auth/register`
- `logout()` — POST `/api/auth/logout`, сбросить `user`
- `fetchMe()` — GET `/api/auth/me`, обновить `user`

Использовать HTTP-клиент из FE-003 (`credentials: 'include'`). Обрабатывать ошибки API, пробрасывать или сохранять для UI.

## Критерии готовности

- Login, register и logout работают согласно контракту backend
- После успешного входа `user` сохраняется, `isAuthenticated` реактивно обновляется
- `fetchMe()` корректно восстанавливает сессию после перезагрузки страницы (если поддерживается backend)
