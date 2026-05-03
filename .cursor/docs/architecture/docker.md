# Docker и окружение

## Docker Compose

Инфраструктура в Docker, код локально.

```yaml
services:
  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: mentor_ai
      POSTGRES_USER: mentor
      POSTGRES_PASSWORD: ${PG_PASSWORD}

  qdrant:
    image: qdrant/qdrant:latest
    restart: unless-stopped
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    ports:
      - "6379:6379"

volumes:
  pg_data:
  qdrant_data:
```

## Запуск инфраструктуры

```bash
docker compose up -d
```

Проверка:

- PostgreSQL: `psql -h localhost -U mentor -d mentor_ai`
- Qdrant: http://localhost:6333/dashboard
- Redis: `redis-cli ping`

## Переменные окружения (.env)

```env
# PostgreSQL
PG_HOST=localhost
PG_PORT=5432
PG_DB=mentor_ai
PG_USER=mentor
PG_PASSWORD=changeme

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Qwen API
QWEN_API_KEY=your_api_key_here
QWEN_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-plus
QWEN_EMBEDDING_MODEL=text-embedding-v3

# App
SECRET_KEY=changeme
SESSION_TTL_HOURS=24
CORS_ORIGINS=http://localhost:5173

# RAG
RAG_TOP_K=5
RAG_SCORE_THRESHOLD=0.7
RAG_CHUNK_SIZE=800
RAG_CHUNK_OVERLAP=100
```

## Полный запуск (dev)

```bash
# 1. Инфраструктура
docker compose up -d

# 2. Backend
cd backend
cp ../.env.example .env   # настроить переменные
pip install -r requirements.txt
alembic upgrade head
uvicorn src.app.main:app --reload --port 8000

# 3. Frontend
cd frontend
npm install
npm run dev
```

Фронтенд: http://localhost:5173

Бэкенд API: http://localhost:8000

Qdrant Dashboard: http://localhost:6333/dashboard
