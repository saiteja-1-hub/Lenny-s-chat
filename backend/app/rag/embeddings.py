import httpx

from app.config import get_settings


async def get_embedding(text: str) -> list[float]:
    """
    Generate an embedding for the supplied text.

    Production:
        OpenAI text-embedding-3-small

    Local development:
        Ollama nomic-embed-text
    """

    settings = get_settings()

    # ============================================================
    # Ollama Embeddings
    # ============================================================

    if settings.embedding_provider == "ollama":
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.ollama_base_url}/api/embeddings",
                json={
                    "model": settings.embedding_model,
                    "prompt": text,
                },
            )

            response.raise_for_status()

            data = response.json()

            embedding = data["embedding"]

            # Verify vector dimension
            if len(embedding) != settings.embedding_dim:
                raise ValueError(
                    f"Embedding dimension mismatch. "
                    f"Expected {settings.embedding_dim}, "
                    f"but Ollama returned {len(embedding)} dimensions."
                )

            return embedding

    # ============================================================
    # OpenAI Embeddings
    # ============================================================

    if settings.embedding_provider == "openai":

        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured."
            )

        async with httpx.AsyncClient(timeout=60.0) as client:

            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": (
                        f"Bearer {settings.openai_api_key}"
                    ),
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.embedding_model,
                    "input": text,
                    "dimensions": settings.embedding_dim,
                },
            )

            response.raise_for_status()

            data = response.json()

            embedding = data["data"][0]["embedding"]

            # Verify vector dimension
            if len(embedding) != settings.embedding_dim:
                raise ValueError(
                    f"Embedding dimension mismatch. "
                    f"Expected {settings.embedding_dim}, "
                    f"but OpenAI returned {len(embedding)} dimensions."
                )

            return embedding

    # ============================================================
    # Unsupported Provider
    # ============================================================

    raise ValueError(
        f"Unsupported embedding provider: "
        f"{settings.embedding_provider}"
    )