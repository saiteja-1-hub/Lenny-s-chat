import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import check_db_health, get_db
from app.models.schemas import HealthOut
from app.rag.embeddings import get_embedding
from app.rag.retriever import TranscriptRetriever

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("", response_model=HealthOut)
async def health(db: AsyncSession = Depends(get_db)):
    settings = get_settings()

    db_ok = await check_db_health()

    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            ollama_ok = resp.status_code == 200
    except httpx.HTTPError:
        ollama_ok = False

    vector_rows = 0
    if db_ok:
        try:
            retriever = TranscriptRetriever(db, get_embedding)
            vector_rows = await retriever.count_indexed_chunks()
        except Exception:  # noqa: BLE001 - table may not exist yet
            vector_rows = 0

    status = "ok" if (db_ok and ollama_ok) else "degraded"
    return HealthOut(status=status, database=db_ok, ollama=ollama_ok, vector_index_rows=vector_rows)
