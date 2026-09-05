from unittest.mock import AsyncMock, MagicMock

import pytest

from app.rag.retriever import TranscriptRetriever


@pytest.mark.asyncio
async def test_retrieve_relevant_chunks_returns_mapped_rows():
    fake_row = MagicMock(
        episode_title="Ep 1",
        guest_name="Jane Doe",
        chunk_text="Some insight about onboarding.",
        timestamp_ref="12:34",
        similarity_score=0.82,
    )
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [fake_row]

    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_result

    async def fake_embedding_fn(text: str) -> list[float]:
        return [0.1, 0.2, 0.3]

    retriever = TranscriptRetriever(mock_session, fake_embedding_fn)
    results = await retriever.retrieve_relevant_chunks("How do I improve onboarding?")

    assert len(results) == 1
    assert results[0]["episode"] == "Ep 1"
    assert results[0]["guest"] == "Jane Doe"
    assert results[0]["score"] == pytest.approx(0.82)


@pytest.mark.asyncio
async def test_retrieve_relevant_chunks_empty_when_no_matches():
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_result

    async def fake_embedding_fn(text: str) -> list[float]:
        return [0.0, 0.0, 0.0]

    retriever = TranscriptRetriever(mock_session, fake_embedding_fn)
    results = await retriever.retrieve_relevant_chunks("completely unrelated out-of-domain query")

    assert results == []
