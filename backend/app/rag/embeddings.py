import httpx

from app.config import get_settings


async def get_embedding(text: str) -> list[float]:
    """
    Generate an embedding for the supplied text.

    Production:
        Gemini gemini-embedding-001

    Local development:
        Ollama nomic-embed-text
    """

    settings = get_settings()

    # ============================================================
    # Ollama
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

            if len(embedding) != settings.embedding_dim:
                raise ValueError(
                    f"Embedding dimension mismatch. "
                    f"Expected {settings.embedding_dim}, "
                    f"but Ollama returned {len(embedding)} dimensions."
                )

            return embedding

    # ============================================================
    # Gemini
    # ============================================================

    if settings.embedding_provider == "gemini":

        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        url = (
            "https://generativelanguage.googleapis.com/"
            "v1beta/models/"
            f"{settings.embedding_model}:embedContent"
        )

        headers = {
            "x-goog-api-key": settings.gemini_api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "model": f"models/{settings.embedding_model}",
            "content": {
                "parts": [
                    {
                        "text": text
                    }
                ]
            },
            "output_dimensionality": settings.embedding_dim,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:

            response = await client.post(
                url,
                headers=headers,
                json=payload,
            )

            response.raise_for_status()

            data = response.json()

            try:
                embedding = data["embedding"]["values"]
            except KeyError:
                raise ValueError(
                    f"Unexpected Gemini embedding response: {data}"
                )

            if len(embedding) != settings.embedding_dim:
                raise ValueError(
                    f"Embedding dimension mismatch. "
                    f"Expected {settings.embedding_dim}, "
                    f"but Gemini returned {len(embedding)} dimensions."
                )

            return embedding

    # ============================================================
    # Unsupported provider
    # ============================================================

    raise ValueError(
        f"Unsupported embedding provider: "
        f"{settings.embedding_provider}"
    )