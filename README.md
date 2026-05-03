# Project Mentor AI

RAG-based ИИ-ассистент для студентов по проектной деятельности. Веб-приложение, в котором студенты могут задавать вопросы по управлению проектами и получать ответы, основанные на проверенной базе знаний, а не на «галлюцинациях» LLM.

## Содержание

- [Описание проекта](#описание-проекта)
- [Стек технологий](#стек-технологий)
- [Архитектура системы](#архитектура-системы)
- [Backend](#backend)
- [Frontend](#frontend)
- [RAG-пайплайн](#rag-пайплайн)
- [База данных](#база-данных)
- [API](#api)
- [Инфраструктура](#инфраструктура)
- [Быстрый старт](#быстрый-старт)
- [Конфигурация](#конфигурация)
- [Makefile-команды](#makefile-команды)

---

## Описание проекта

Студенты, работая над проектами, часто сталкиваются не с техническими, а с **методологическими** трудностями: как планировать задачи, вести документацию, распределять роли, применять Agile/Scrum практики.

**Project Mentor AI** — это «карманный ментор», который:

- отвечает **только на основе проверенной базы знаний** (статьи, книги, ГОСТы, практики Agile, Scrum, DevOps);
- показывает **источники**, на которых основан каждый ответ;
- **стримит** ответы в реальном времени через SSE;
- хранит **историю диалогов** и учитывает контекст беседы;
- поддерживает **админ-панель** для управления документами базы знаний.

### Примеры вопросов

- «Как правильно составить ТЗ?»
- «Какие этапы у Scrum?»
- «Как распределить роли в команде?»
- «Что такое Definition of Done?»

---

## Стек технологий

| Компонент | Технология |
|---|---|
| Язык бэкенда | Python 3.12+ |
| Backend-фреймворк | Litestar (async) |
| Frontend | Vue 3 + Vite 8 + Pinia 3 + Vue Router 4 |
| LLM-провайдер | OpenRouter (любая модель с OpenAI-совместимым API) |
| Embedding-провайдер | OpenRouter / любой OpenAI-совместимый API |
| Реляционная БД | PostgreSQL 16 |
| Векторная БД | Qdrant |
| Кеш / Сессии | Redis 7 (через Cashews) |
| ORM / Миграции | SQLAlchemy 2.0 (async) + Alembic |
| RAG-пайплайн | Собственная реализация (без LangChain / LlamaIndex) |
| Авторизация | Cookie-based сессии на Redis (HttpOnly) |
| Стриминг ответов | SSE (Server-Sent Events) |
| Инфраструктура | Docker Compose |
| Линтеры | Ruff, mypy |
| Тестирование | pytest + pytest-asyncio + pytest-cov |
| Логирование | structlog (JSON) |
| HTTP-клиент | httpx (async) |
| Markdown-рендеринг | marked + DOMPurify |

---

## Архитектура системы

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser (SPA)                           │
│                     Vue 3 + Vite + Pinia                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │  HTTP / SSE
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Litestar API Server                        │
│              REST endpoints + SSE streaming                     │
│           SessionMiddleware (cookie → Redis)                    │
├─────────┬──────────┬──────────┬─────────────┬───────────────────┤
│  Auth   │  Users   │  Chats   │     RAG     │   Admin (planned) │
│  View   │  View    │  View    │   Manager   │                   │
└────┬────┴────┬─────┴────┬─────┴──────┬──────┴───────────────────┘
     │         │          │            │
     ▼         ▼          ▼            ▼
┌─────────┐ ┌──────┐ ┌──────────┐ ┌────────────────────┐
│  Redis  │ │  PG  │ │    PG    │ │   LLM API          │
│Sessions │ │Users │ │Chats/Msgs│ │ (OpenRouter / any)  │
└─────────┘ └──────┘ └──────────┘ └────────────────────┘
                                           │
                                  ┌────────┴────────┐
                                  │  Embedding API   │
                                  │ (OpenRouter/any) │
                                  └────────┬─────────┘
                                           │
                                  ┌────────▼─────────┐
                                  │     Qdrant       │
                                  │  (vector search) │
                                  └──────────────────┘
```

### Поток обработки вопроса

1. Пользователь отправляет вопрос через UI
2. Frontend делает POST-запрос на `/api/chats/{id}/messages`
3. Backend сохраняет сообщение пользователя в PostgreSQL
4. RAG Manager получает вопрос и историю диалога (последние 10 сообщений)
5. Embedding API превращает вопрос в вектор
6. Qdrant ищет top-K релевантных фрагментов базы знаний
7. Формируется промпт с системной инструкцией, контекстом из БЗ и историей
8. LLM API стримит ответ токен за токеном
9. Backend пробрасывает токены клиенту через SSE-события
10. По завершении отправляются источники и ответ сохраняется в БД

---

## Backend

### Структура модулей

```
backend/
├── app/
│   ├── __main__.py              # Click CLI: точка входа (python -m app ...)
│   ├── entrypoints/
│   │   ├── api/
│   │   │   ├── app.py           # Litestar create_app(), роуты, CORS, middleware
│   │   │   └── daemon.py        # Uvicorn runner
│   │   └── seed_knowledge_base.py  # Загрузка документов в Qdrant
│   │
│   ├── auth/                    # Модуль аутентификации
│   │   ├── views.py             # AuthView: register, login, logout
│   │   ├── manager.py           # Бизнес-логика авторизации
│   │   ├── accessor.py          # SessionAccessor (Redis)
│   │   └── domain/
│   │       └── schemas.py       # LoginRequest, RegisterRequest (Pydantic)
│   │
│   ├── users/                   # Модуль пользователей
│   │   ├── views.py             # UserView: GET /api/users/me
│   │   ├── manager.py           # UserManager
│   │   ├── accessor.py          # UserAccessor (PostgreSQL)
│   │   ├── db.py                # UserModel (SQLAlchemy ORM)
│   │   └── domain/
│   │       └── schemas.py       # UserResponse
│   │
│   ├── chat/                    # Модуль чатов
│   │   ├── views.py             # ChatView: CRUD чатов, отправка сообщений (SSE)
│   │   ├── manager.py           # ChatManager: оркестрация RAG + сохранение
│   │   ├── accessor.py          # ChatAccessor (PostgreSQL)
│   │   ├── db.py                # ChatModel, MessageModel (ORM)
│   │   ├── exceptions.py        # ChatNotFoundError
│   │   └── domain/
│   │       └── schemas.py       # ChatResponse, MessageResponse, SendMessageRequest
│   │
│   ├── rag/                     # RAG-пайплайн
│   │   ├── manager.py           # RAGManager: embed → search → prompt → stream
│   │   ├── config.py            # RAGConfig, LLMProviderConfig, QdrantConfig
│   │   ├── chunker.py           # Разбиение документов на чанки
│   │   └── accessors/
│   │       ├── embedder.py      # EmbedderAccessor (OpenAI-совместимый API)
│   │       ├── retriever.py     # RetrieverAccessor (Qdrant)
│   │       └── llm.py           # LLMAccessor (OpenAI-совместимый API, streaming)
│   │
│   ├── documents/               # Модель документов
│   │   └── db.py                # DocumentModel (ORM)
│   │
│   ├── store/                   # Хранилища данных
│   │   ├── store.py             # Store — центральный DI-контейнер
│   │   ├── pg/                  # PostgreSQL
│   │   │   ├── accessor.py      # PgAccessor (async sessionmaker)
│   │   │   ├── config.py        # DSN из конфига
│   │   │   └── migrations/      # Alembic миграции
│   │   └── cache.py             # CacheAccessor (Redis через Cashews)
│   │
│   ├── web/                     # HTTP-инфраструктура
│   │   ├── middlewares.py       # SessionMiddleware (cookie-based auth)
│   │   ├── errors.py            # Обработчики ошибок
│   │   └── request.py           # AppRequest с данными сессии
│   │
│   ├── common/                  # Общие утилиты
│   │   ├── config.py            # StaticConfig (константы, системный промпт)
│   │   └── sse.py               # Хелперы для SSE-событий
│   │
│   ├── base/                    # Базовые классы
│   │   ├── accessor.py          # BaseAccessor
│   │   ├── manager.py           # BaseManager
│   │   └── view.py              # BaseView
│   │
│   └── global_/                 # Глобальные настройки
│       ├── settings.py          # Загрузка YAML + env vars (APP_* с __ разделителем)
│       ├── log.py               # Настройка structlog
│       └── autodiscover.py      # Автоматический поиск CLI-команд
│
├── tests/                       # Тесты
│   ├── config.yaml              # Конфиг для тестов
│   ├── unit/                    # Юнит-тесты
│   └── integration/             # Интеграционные тесты
│
├── pyproject.toml               # Зависимости и настройки (ruff, mypy, pytest)
└── Makefile                     # Команды разработки
```

### Паттерны

- **Accessor** — слой доступа к данным (PostgreSQL, Redis, Qdrant, LLM API). Каждый Accessor наследуется от `BaseAccessor`, имеет методы `connect()` и `disconnect()`.
- **Manager** — бизнес-логика. Работает через Store, не обращается к БД напрямую.
- **View** — Litestar class-based контроллеры. Тонкий слой: валидация → делегирование Manager → формирование ответа.
- **Store** — центральный DI-контейнер. Создаёт и хранит все Accessor'ы и Manager'ы. Управляет их жизненным циклом (connect/disconnect при старте/остановке приложения).

### Конфигурация

Конфигурация загружается каскадно (каждый следующий источник перезаписывает предыдущий):

1. `etc/config.yaml` — базовый конфиг
2. Файл из переменной `CONFIG` или `local/etc/config.yaml` — локальные переопределения
3. Переменные окружения с префиксом `APP_` и разделителем `__` (например, `APP_STORE__DATABASE__HOST=localhost`)

### Авторизация

- Cookie-based сессии, хранящиеся в Redis
- Cookie `session_id` (HttpOnly, SameSite=Lax, Secure)
- TTL сессии: 24 часа
- `SessionMiddleware` проверяет cookie на каждом запросе (кроме `/api/auth/*`, `/api/health`, `/docs`)
- Роли: `user`, `admin`

---

## Frontend

### Структура

```
frontend/
├── index.html                   # Точка входа (lang="ru"), Inter font
├── vite.config.js               # Vite: порт 5173, прокси /api → localhost:8000
├── package.json                 # Зависимости
│
└── src/
    ├── main.js                  # Инициализация Vue + Pinia + Router
    ├── App.vue                  # Корневой компонент (CosmicBackground + router-view)
    │
    ├── router/
    │   └── index.js             # Маршруты + navigation guards
    │
    ├── pages/                   # Страницы приложения
    │   ├── LoginPage.vue        # Форма входа
    │   ├── RegisterPage.vue     # Форма регистрации
    │   ├── ChatPage.vue         # Главная — чат с ассистентом
    │   └── AdminPage.vue        # Админ-панель (управление документами)
    │
    ├── components/              # UI-компоненты
    │   └── CosmicBackground.vue # Анимированный фон (тёмная «космическая» тема)
    │
    ├── stores/                  # Pinia stores (state management)
    │   ├── auth.js              # Состояние авторизации (user, isAdmin)
    │   ├── chat.js              # Чаты, сообщения, SSE-стриминг
    │   └── admin.js             # Управление документами
    │
    ├── api/                     # HTTP-клиенты
    │   ├── client.js            # Базовый клиент (fetch, credentials: include, SSE)
    │   ├── auth.js              # register, login, logout, getMe
    │   ├── chat.js              # CRUD чатов, отправка сообщений
    │   └── admin.js             # API админ-панели
    │
    └── assets/styles/           # Стили
        ├── main.css             # Основные стили
        ├── reset.css            # CSS reset
        ├── base.css             # Базовые стили
        ├── variables.css        # CSS-переменные (цвета, отступы)
        ├── utilities.css        # Утилитарные классы
        └── animations.css       # Анимации
```

### Маршрутизация

| Путь | Компонент | Доступ |
|---|---|---|
| `/login` | `LoginPage.vue` | Только для гостей |
| `/register` | `RegisterPage.vue` | Только для гостей |
| `/` | Редирект → `/chat` | — |
| `/chat` | `ChatPage.vue` | Авторизованные |
| `/chat/:id` | `ChatPage.vue` | Авторизованные |
| `/admin` | `AdminPage.vue` | Только admin |

Navigation guards автоматически:
- Перенаправляют неавторизованных на `/login`
- Перенаправляют не-админов с `/admin` на `/chat`
- Перенаправляют авторизованных с `/login` и `/register` на `/chat`

### State Management (Pinia)

**auth store** — управление состоянием авторизации:
- `user` — текущий пользователь (или `null`)
- `isAuthenticated`, `isAdmin` — computed-свойства
- `login()`, `register()`, `logout()`, `fetchMe()`

**chat store** — управление чатами и сообщениями:
- `chats` — список чатов пользователя
- `messages` — сообщения текущего чата
- `isStreaming` — флаг активного стриминга
- `sendMessage()` — отправка с SSE-обработкой (события: `token`, `sources`, `done`, `error`, `no_data`)
- `createChat()`, `deleteChat()`, `selectChat()`, `fetchMessages()`

**admin store** — управление документами базы знаний:
- Загрузка, просмотр и удаление документов

### SSE-обработка на клиенте

Frontend читает SSE-поток через `ReadableStream` API:

1. POST-запрос на `/api/chats/{id}/messages` возвращает `text/event-stream`
2. Клиент парсит SSE-события из потока:
   - `event: token` → добавляет токен к ответу ассистента
   - `event: sources` → прикрепляет JSON-массив источников к сообщению
   - `event: done` → завершение стриминга
   - `event: error` / `event: no_data` → отображение ошибки / уведомления

### UI/UX

- Тёмная «космическая» тема с анимированным фоном
- Рендеринг Markdown в ответах ассистента (marked + DOMPurify для защиты от XSS)
- Адаптивная вёрстка

---

## RAG-пайплайн

Реализован **с нуля**, без использования LangChain или LlamaIndex.

### Компоненты

```
┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│   Chunker    │────▶│   Embedder    │────▶│   Qdrant     │
│ (split docs) │     │ (Embedding API)│    │  (upsert)    │
└──────────────┘     └───────────────┘     └──────────────┘

┌──────────────┐     ┌───────────────┐     ┌──────────────┐     ┌──────────┐
│  User query  │────▶│   Embedder    │────▶│  Retriever   │────▶│   LLM    │
│              │     │ (Embedding API)│    │  (Qdrant)    │     │ (stream) │
└──────────────┘     └───────────────┘     └──────────────┘     └──────────┘
```

### Этап индексации (seed)

1. Чтение документов из `knowledge_base/` (поддерживаемые форматы: `.pdf`, `.docx`, `.md`, `.txt`)
2. Разбиение на чанки (`chunk_size=512`, `chunk_overlap=64`)
3. Генерация embeddings через Embedding API (батчами до 256)
4. Загрузка в Qdrant (коллекция `knowledge_base`, cosine distance)
5. Сохранение метаданных документов в PostgreSQL (таблица `documents`)

### Этап ответа (query)

1. **Embedding**: вопрос пользователя → вектор (Embedding API)
2. **Retrieval**: поиск top-K ближайших чанков в Qdrant (`top_k=5`, `score_threshold=0.15`)
3. **No-data check**: если ничего не найдено → SSE-событие `no_data` с предложением переформулировать вопрос
4. **Prompt building**: системный промпт + контекст из найденных чанков + история диалога (до 10 сообщений) + вопрос пользователя
5. **Generation**: LLM API стримит ответ токен за токеном
6. **Sources**: после завершения генерации отправляются метаданные источников (название документа, фрагмент текста, score)

### Системный промпт

> Ты — ИИ-ассистент для студентов по проектной деятельности. Отвечай только на основе предоставленного контекста. Если в контексте нет информации для ответа, честно скажи об этом и предложи переформулировать вопрос. В конце ответа укажи, из каких источников взята информация. Пиши простым языком, без лишних терминов.

### Параметры RAG (по умолчанию)

| Параметр | Значение | Описание |
|---|---|---|
| `top_k` | 5 | Количество фрагментов для поиска |
| `score_threshold` | 0.15 | Минимальный порог релевантности |
| `chunk_size` | 512 | Размер чанка (в символах) |
| `chunk_overlap` | 64 | Перекрытие между чанками |
| `history_window` | 10 | Сколько последних сообщений учитывать в контексте |

---

## База данных

### Схема PostgreSQL

```
┌──────────────────────────┐       ┌──────────────────────────┐
│          users           │       │        documents         │
├──────────────────────────┤       ├──────────────────────────┤
│ id         UUID PK       │       │ id          UUID PK      │
│ username   VARCHAR UNIQUE│       │ filename    VARCHAR       │
│ email      VARCHAR UNIQUE│       │ title       VARCHAR       │
│ password_hash VARCHAR    │       │ status      VARCHAR       │
│ role       VARCHAR       │       │ chunk_count INTEGER       │
│ created_at TIMESTAMP     │       │ created_at  TIMESTAMP     │
│ updated_at TIMESTAMP     │       │ updated_at  TIMESTAMP     │
└──────────┬───────────────┘       └──────────────────────────┘
           │ 1:N
           ▼
┌──────────────────────────┐
│          chats           │
├──────────────────────────┤
│ id         UUID PK       │
│ user_id    UUID FK→users │
│ title      VARCHAR NULL  │
│ created_at TIMESTAMP     │
│ updated_at TIMESTAMP     │
└──────────┬───────────────┘
           │ 1:N
           ▼
┌──────────────────────────┐
│        messages          │
├──────────────────────────┤
│ id         UUID PK       │
│ chat_id    UUID FK→chats │
│ role       VARCHAR       │
│            (user/assistant/system) │
│ content    TEXT           │
│ sources    JSONB NULL     │
│ created_at TIMESTAMP     │
└──────────────────────────┘
```

### Redis

- Хранение сессий: ключ `session:{uuid}`, значение — JSON с `user_id` и `role`
- TTL: 24 часа

### Qdrant

- Коллекция: `knowledge_base`
- Метрика: cosine distance
- Payload полей: `document_title`, `content`, `document_id`, `chunk_index`

---

## API

Базовый URL: `/api`

### Аутентификация

| Метод | Эндпоинт | Описание |
|---|---|---|
| POST | `/api/auth/register` | Регистрация (201) |
| POST | `/api/auth/login` | Вход (устанавливает cookie `session_id`) |
| POST | `/api/auth/logout` | Выход (удаляет cookie) |

### Пользователи

| Метод | Эндпоинт | Описание |
|---|---|---|
| GET | `/api/users/me` | Текущий пользователь |

### Чаты

| Метод | Эндпоинт | Описание |
|---|---|---|
| GET | `/api/chats/` | Список чатов пользователя |
| POST | `/api/chats/` | Создать чат (201) |
| GET | `/api/chats/{chat_id}` | Получить чат |
| DELETE | `/api/chats/{chat_id}` | Удалить чат (204) |
| GET | `/api/chats/{chat_id}/messages` | Сообщения чата (`?offset=0&limit=50`) |
| POST | `/api/chats/{chat_id}/messages` | Отправить сообщение → SSE-стрим ответа |

### Health Check

| Метод | Эндпоинт | Описание |
|---|---|---|
| GET | `/api/health` | Статус PG, Redis, Qdrant (200 / 503) |

### SSE-события при отправке сообщения

| Событие | Данные | Описание |
|---|---|---|
| `token` | Фрагмент текста | Токен ответа ассистента |
| `sources` | JSON-массив | Источники: `document_title`, `content`, `score` |
| `done` | — | Завершение стриминга |
| `no_data` | Текст сообщения | Информация не найдена в базе знаний |
| `error` | Текст ошибки | Ошибка при обработке запроса |

### Документация API

Swagger UI доступен по адресу `/docs` при запущенном сервере.

---

## Инфраструктура

### Docker Compose

Инфраструктурные сервисы запускаются через `docker-compose.yaml`:

| Сервис | Образ | Порт (host:container) |
|---|---|---|
| PostgreSQL | `postgres:16-alpine` | `5433:5432` |
| Redis | `redis:7-alpine` | `6379:6379` |
| Qdrant | `qdrant/qdrant:latest` | `6333:6333`, `6334:6334` |

Данные PostgreSQL и Qdrant сохраняются в Docker volumes (`pg_data`, `qdrant_data`).

---

## Быстрый старт

### Предварительные требования

- Python 3.12+
- Node.js 18+
- Docker и Docker Compose

### 1. Запуск инфраструктуры

```bash
docker compose up -d
```

### 2. Настройка бэкенда

```bash
cd backend

# Создание виртуального окружения и установка зависимостей
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Создание конфига
mkdir -p local/etc
cat > local/etc/config.yaml << 'EOF'
app:
  secret_key: "your-secret-key-change-in-production"
  session_ttl_hours: 24

store:
  database:
    host: localhost
    port: 5433
    name: mentor_ai
    user: postgres
    password: postgres
  cache:
    host: localhost
    port: 6379

qdrant:
  host: localhost
  port: 6333

llm:
  api_key: "your-openrouter-api-key"
  api_base_url: "https://openrouter.ai/api/v1"
  model: "qwen/qwen3-235b-a22b"
  embedding_model: "qwen/qwen3-235b-a22b"

rag:
  top_k: 5
  score_threshold: 0.15
  chunk_size: 512
  chunk_overlap: 64

cors:
  origins: "http://localhost:5173"
EOF

# Применение миграций
make upgrade

# Загрузка базы знаний в Qdrant
make seed

# Запуск API-сервера
make api
```

### 3. Настройка фронтенда

```bash
cd frontend

# Установка зависимостей
npm install

# Запуск dev-сервера
npm run dev
```

### 4. Открыть приложение

Перейти на http://localhost:5173

---

## Конфигурация

### Пример конфигурации (YAML)

```yaml
app:
  secret_key: "change-me"
  session_ttl_hours: 24

store:
  database:
    host: localhost
    port: 5433
    name: mentor_ai
    user: postgres
    password: postgres
  cache:
    host: localhost
    port: 6379

qdrant:
  host: localhost
  port: 6333

llm:
  api_key: "your-api-key"
  api_base_url: "https://openrouter.ai/api/v1"  # или любой OpenAI-совместимый API
  model: "qwen/qwen3-235b-a22b"                 # любая модель провайдера
  embedding_model: "qwen/qwen3-235b-a22b"       # модель для embeddings

rag:
  top_k: 5
  score_threshold: 0.15
  chunk_size: 512
  chunk_overlap: 64

cors:
  origins: "http://localhost:5173"
```

### Переменные окружения

Любой параметр YAML-конфига можно переопределить через env-переменную с префиксом `APP_` и разделителем `__`:

| Переменная | Соответствует |
|---|---|
| `APP_STORE__DATABASE__HOST` | `store.database.host` |
| `APP_STORE__DATABASE__PORT` | `store.database.port` |
| `APP_STORE__CACHE__HOST` | `store.cache.host` |
| `APP_LLM__API_KEY` | `llm.api_key` |
| `APP_LLM__API_BASE_URL` | `llm.api_base_url` |
| `APP_LLM__MODEL` | `llm.model` |
| `APP_LLM__EMBEDDING_MODEL` | `llm.embedding_model` |
| `CONFIG` | Путь к YAML-файлу конфигурации |
| `DEBUG` | Включить debug-режим |

---

## Makefile-команды

Выполняются из директории `backend/`:

| Команда | Описание |
|---|---|
| `make api` | Запуск API-сервера (uvicorn) |
| `make seed` | Загрузка базы знаний в Qdrant |
| `make upgrade` | Применить все миграции Alembic |
| `make downgrade` | Откатить миграцию |
| `make revision` | Создать новую миграцию (autogenerate) |
| `make lint` | Проверка кода (ruff check) |
| `make fix` | Автофикс линтера (ruff --fix) |
| `make style` | Форматирование кода (ruff format) |
| `make mypy` | Проверка типов (mypy) |
| `make test` | Запуск всех тестов |
| `make test-unit` | Только юнит-тесты |
| `make test-integration` | Только интеграционные тесты |
| `make test-cov` | Тесты с отчётом о покрытии |
