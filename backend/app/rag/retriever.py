from typing import Any, Callable, Awaitable

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings

EmbeddingFn = Callable[[str], Awaitable[list[float]]]


class TranscriptRetriever:
    def __init__(self, session: AsyncSession, embedding_fn: EmbeddingFn):
        self.session = session
        self.embedding_fn = embedding_fn

    async def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int | None = None,
        similarity_threshold: float | None = None,
    ) -> list[dict[str, Any]]:
        settings = get_settings()
        top_k = top_k or settings.top_k
        similarity_threshold = (
            similarity_threshold if similarity_threshold is not None else settings.similarity_threshold
        )

        query_vector = await self.embedding_fn(query)

        # Note: we use CAST(:vector AS vector) rather than ":vector::vector" —
        # SQLAlchemy's bind-parameter parser misreads a named param immediately
        # followed by "::" as a syntax error, so CAST() sidesteps that entirely.
        query_stmt = text(
            """
            SELECT
                episode_title,
                guest_name,
                chunk_text,
                timestamp_ref,
                1 - (embedding <=> CAST(:vector AS vector)) AS similarity_score
            FROM transcript_chunks
            WHERE 1 - (embedding <=> CAST(:vector AS vector)) >= :threshold
            ORDER BY similarity_score DESC
            LIMIT :limit;
            """
        )

        result = await self.session.execute(
            query_stmt,
            {"vector": str(query_vector), "threshold": similarity_threshold, "limit": top_k},
        )
        rows = result.fetchall()

        return [
            {
                "episode": r.episode_title,
                "guest": r.guest_name,
                "text": r.chunk_text,
                "timestamp": r.timestamp_ref,
                "score": float(r.similarity_score),
            }
            for r in rows
        ]

    async def count_indexed_chunks(self) -> int:
        result = await self.session.execute(text("SELECT COUNT(*) FROM transcript_chunks"))
        return result.scalar_one()