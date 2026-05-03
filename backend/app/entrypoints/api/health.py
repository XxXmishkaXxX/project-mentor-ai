from litestar import MediaType, Response, get
from sqlalchemy import text

from app import global_store


@get("/api/health")
async def health_check() -> Response[dict[str, str]]:
    store = global_store.get()
    statuses: dict[str, str] = {}

    try:
        async with store.pg.session() as session:
            await session.execute(text("SELECT 1"))
        statuses["pg"] = "ok"
    except Exception:  # noqa: BLE001
        statuses["pg"] = "error"

    try:
        await store.cache.client.get("_health_check")
        statuses["redis"] = "ok"
    except Exception:  # noqa: BLE001
        statuses["redis"] = "error"

    if store.is_rag_available:
        try:
            await store.retriever.client.get_collections()
            statuses["qdrant"] = "ok"
        except Exception:  # noqa: BLE001
            statuses["qdrant"] = "error"

    all_ok = all(v == "ok" for v in statuses.values())
    return Response(
        content=statuses,
        status_code=200 if all_ok else 503,
        media_type=MediaType.JSON,
    )
