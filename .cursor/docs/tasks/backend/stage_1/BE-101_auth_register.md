# BE-101: Auth — регистрация

**Приоритет**: Must have
**Этап**: 1
**US**: US-01
**Зависимости**: BE-005
**Статус**: не начата

## Описание

Реализовать регистрацию пользователя: валидация входных данных, хеширование пароля (bcrypt), создание записи в таблице `users`.

## Файлы

- `backend/src/app/auth/schemas.py` — DTO регистрации (`RegisterDTO`) и ответ пользователя
- `backend/src/app/auth/service.py` — `hash_password`, `create_user`
- `backend/src/app/auth/controller.py` — endpoint `POST /api/auth/register`

## Реализация

- `RegisterDTO`: `username` str (3–50 символов), `email` EmailStr, `password` str (минимум 8 символов).
- Сервис: `hash_password` через bcrypt; `create_user` — INSERT в `users`.
- Контроллер: `POST /api/auth/register`, ответ `UserResponse` (`id`, `username`, `email`, `role`), статус 201.
- Обработка `IntegrityError` при дубликате email/username → HTTP 409.

## Критерии готовности

- Успешная регистрация создаёт запись в `users`
- Дубликат email или username → 409
- Пустые/невалидные поля → 422
