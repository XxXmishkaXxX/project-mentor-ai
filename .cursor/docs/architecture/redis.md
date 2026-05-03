# Кеш и сессии: Redis 7

## Назначение

1. **Хранение сессий авторизации** — основное применение
2. **Кеш ответов** (опционально) — для частых одинаковых запросов

## Развёртывание

```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
```

## Сессии

| Ключ | Значение | TTL |
|------|----------|-----|
| `session:{session_id}` | `{"user_id": "uuid", "role": "student", "created_at": "..."}` | 24 часа |

### Логика работы

1. При логине backend генерирует `session_id` (UUID4 или `secrets.token_urlsafe(32)`)
2. Сохраняет в Redis: `SET session:{session_id} {json_payload} EX 86400`
3. Отправляет клиенту: `Set-Cookie: session_id={value}; HttpOnly; Path=/; SameSite=Lax`
4. При каждом запросе Session Middleware:
   - Читает cookie `session_id`
   - Делает `GET session:{session_id}` в Redis
   - Если найдено — достаёт user_id и role, передаёт в handler
   - Если не найдено — 401 Unauthorized
5. При логауте: `DEL session:{session_id}` + очистка cookie

### Безопасность cookie

- `HttpOnly` — не доступна из JavaScript (защита от XSS)
- `SameSite=Lax` — защита от CSRF
- `Secure` — только по HTTPS (в production)
- `Path=/` — доступна для всех путей

## Кеш ответов (опционально)

| Ключ | Значение | TTL |
|------|----------|-----|
| `cache:query:{sha256(query)}` | JSON с ответом и источниками | 1 час |

Кеширование ответов RAG-пайплайна для повторяющихся вопросов. Снижает нагрузку на LLM API и ускоряет ответ.

## Python-клиент

```python
import redis.asyncio as redis

pool = redis.ConnectionPool.from_url("redis://localhost:6379")
client = redis.Redis(connection_pool=pool)
```
