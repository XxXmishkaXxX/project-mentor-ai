class StaticConfig:
    SESSION_TTL_HOURS = 24
    SESSION_COOKIE_NAME = "session_id"
    SESSION_PREFIX = "session:"

    SQL_STR_LEN_SMALL = 20
    SQL_STR_LEN_MEDIUM = 50
    SQL_STR_LEN_LARGE = 100
    SQL_STR_LEN_XLARGE = 255
    SQL_STR_LEN_TEXT = 500

    MAX_CHAT_TITLE_LENGTH = 100
    CHAT_HISTORY_WINDOW = 10

    SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(
        {".pdf", ".docx", ".md", ".txt"},
    )
    EMBEDDING_MAX_BATCH_SIZE = 256
    QDRANT_COLLECTION_NAME = "knowledge_base"

    HTTP_RETRY_CODES: frozenset[int] = frozenset({429, 503})
    HTTP_MAX_RETRIES = 3
    HTTP_BASE_RETRY_DELAY = 1.0
    EMBEDDER_TIMEOUT = 30.0
    LLM_STREAM_TIMEOUT = 120.0
    LLM_CONNECT_TIMEOUT = 15.0

    SYSTEM_PROMPT = (
        "Ты — ИИ-ассистент для студентов по проектной деятельности. "
        "Отвечай только на основе предоставленного контекста. "
        "Если в контексте нет информации для ответа, честно скажи об этом "
        "и предложи переформулировать вопрос. "
        "В конце ответа укажи, из каких источников взята информация. "
        "Пиши простым языком, без лишних терминов."
    )
