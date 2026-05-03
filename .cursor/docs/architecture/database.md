# База данных: PostgreSQL 16

## Таблицы

### users

| Колонка | Тип | Ограничения |
|---------|-----|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() |
| username | VARCHAR(50) | UNIQUE, NOT NULL |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| role | VARCHAR(20) | NOT NULL, DEFAULT 'student' |
| created_at | TIMESTAMPTZ | DEFAULT now() |
| updated_at | TIMESTAMPTZ | DEFAULT now() |

Роли: `student`, `admin`

### chats

| Колонка | Тип | Ограничения |
|---------|-----|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() |
| user_id | UUID | FK -> users(id) ON DELETE CASCADE, NOT NULL |
| title | VARCHAR(255) | Автогенерация из первого вопроса |
| created_at | TIMESTAMPTZ | DEFAULT now() |
| updated_at | TIMESTAMPTZ | DEFAULT now() |

Индексы: `idx_chats_user_id` на user_id

### messages

| Колонка | Тип | Ограничения |
|---------|-----|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() |
| chat_id | UUID | FK -> chats(id) ON DELETE CASCADE, NOT NULL |
| role | VARCHAR(20) | NOT NULL |
| content | TEXT | NOT NULL |
| sources | JSONB | NULL (только для assistant) |
| created_at | TIMESTAMPTZ | DEFAULT now() |

Роли: `user`, `assistant`

Формат sources:

```json
[
  {
    "document_id": "uuid",
    "document_title": "Scrum Guide 2020",
    "chunk_text": "Sprint Backlog — это набор элементов...",
    "score": 0.92
  }
]
```

Индексы: `idx_messages_chat_id` на chat_id

### feedback

| Колонка | Тип | Ограничения |
|---------|-----|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() |
| message_id | UUID | FK -> messages(id) ON DELETE CASCADE, NOT NULL |
| user_id | UUID | FK -> users(id) ON DELETE CASCADE, NOT NULL |
| is_helpful | BOOLEAN | NOT NULL |
| comment | TEXT | NULL |
| created_at | TIMESTAMPTZ | DEFAULT now() |

UNIQUE(message_id, user_id)

### documents

| Колонка | Тип | Ограничения |
|---------|-----|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() |
| filename | VARCHAR(255) | NOT NULL |
| title | VARCHAR(255) | NOT NULL |
| description | TEXT | NULL |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' |
| error_message | TEXT | NULL |
| file_path | VARCHAR(500) | NOT NULL |
| chunk_count | INTEGER | DEFAULT 0 |
| uploaded_by | UUID | FK -> users(id), NULL |
| created_at | TIMESTAMPTZ | DEFAULT now() |
| updated_at | TIMESTAMPTZ | DEFAULT now() |

Статусы: `pending` -> `processing` -> `indexed` | `error`

## ER-диаграмма

```mermaid
erDiagram
    users {
        uuid id PK
        varchar username UK
        varchar email UK
        varchar password_hash
        varchar role
        timestamptz created_at
        timestamptz updated_at
    }

    chats {
        uuid id PK
        uuid user_id FK
        varchar title
        timestamptz created_at
        timestamptz updated_at
    }

    messages {
        uuid id PK
        uuid chat_id FK
        varchar role
        text content
        jsonb sources
        timestamptz created_at
    }

    feedback {
        uuid id PK
        uuid message_id FK
        uuid user_id FK
        boolean is_helpful
        text comment
        timestamptz created_at
    }

    documents {
        uuid id PK
        varchar filename
        varchar title
        text description
        varchar status
        text error_message
        varchar file_path
        integer chunk_count
        uuid uploaded_by FK
        timestamptz created_at
        timestamptz updated_at
    }

    users ||--o{ chats : "has"
    chats ||--o{ messages : "contains"
    messages ||--o| feedback : "rated by"
    users ||--o{ feedback : "gives"
    users ||--o{ documents : "uploads"
```

## ORM

SQLAlchemy 2.0 (async) + Alembic для миграций. Модели в `backend/src/app/db/models.py`.

## Подключение

PostgreSQL 16 запускается в Docker. Подключение через asyncpg:

```
postgresql+asyncpg://mentor:password@localhost:5432/mentor_ai
```
