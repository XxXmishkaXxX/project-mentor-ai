# Backend: Litestar (Python 3.12)

## Фреймворк

Litestar — async Python web framework. Выбран за:

- Нативная поддержка async/await
- Встроенная поддержка SSE (Server-Sent Events)
- Автогенерация OpenAPI-документации
- Dependency injection
- Pydantic DTO из коробки

## Структура backend

```
backend/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py                 # Litestar app: роутеры, middleware, lifespan
│       ├── config.py               # Pydantic Settings (env vars)
│       ├── db/
│       │   ├── __init__.py
│       │   ├── base.py             # SQLAlchemy async engine + sessionmaker
│       │   └── models.py           # ORM-модели: User, Chat, Message, Feedback, Document
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── controller.py       # POST /register, /login, /logout; GET /me
│       │   ├── schemas.py          # RegisterDTO, LoginDTO, UserResponse
│       │   ├── service.py          # hash_password, verify_password, create_session
│       │   └── middleware.py       # SessionAuthMiddleware: cookie -> Redis -> user
│       ├── chat/
│       │   ├── __init__.py
│       │   ├── controller.py       # CRUD чатов, POST message (SSE)
│       │   ├── schemas.py          # ChatDTO, MessageDTO, SendMessageDTO
│       │   └── service.py          # create_chat, send_message, get_history
│       ├── feedback/
│       │   ├── __init__.py
│       │   ├── controller.py       # POST /messages/{id}/feedback
│       │   ├── schemas.py          # FeedbackDTO
│       │   └── service.py          # save_feedback
│       ├── admin/
│       │   ├── __init__.py
│       │   ├── controller.py       # GET/POST/DELETE /admin/documents
│       │   ├── schemas.py          # DocumentDTO, UploadResponse
│       │   └── service.py          # upload_document, delete_document, reindex
│       └── rag/
│           ├── __init__.py
│           ├── chunker.py          # parse_file, split_into_chunks
│           ├── embedder.py         # embed_text, embed_batch
│           ├── retriever.py        # search_similar (Qdrant)
│           ├── llm.py              # stream_completion (Qwen API)
│           └── pipeline.py         # ask: embed -> search -> prompt -> stream
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/
│   ├── test_auth.py
│   ├── test_chat.py
│   ├── test_rag.py
│   └── test_quality.py            # 20+ тестовых вопросов
├── scripts/
│   └── seed_knowledge_base.py     # Начальная загрузка документов
├── pyproject.toml
└── requirements.txt
```

## Зависимости

- litestar
- uvicorn
- sqlalchemy[asyncio]
- asyncpg
- alembic
- redis[hiredis]
- qdrant-client
- httpx
- pydantic
- pydantic-settings
- bcrypt
- python-multipart
- pypdf2
- python-docx

## Паттерны

Каждый модуль (auth, chat, feedback, admin) имеет одинаковую структуру:

- `controller.py` — Litestar route handlers (тонкий слой, делегирует в service)
- `schemas.py` — Pydantic DTO для входящих и исходящих данных
- `service.py` — бизнес-логика, работа с БД и внешними сервисами

## Конфигурация

Через Pydantic Settings (`config.py`): все параметры читаются из переменных окружения / .env файла. Подробнее в [docker.md](docker.md).

## Запуск

```bash
cd backend
pip install -r requirements.txt
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```
