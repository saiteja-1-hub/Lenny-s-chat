import httpx

from app.config import get_settings

_local_model = None


def _get_local_model():
    global _local_model
    if _local_model is None:
        from sentence_transformers import SentenceTransformer  # optional dependency

        _local_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _local_model


async def get_embedding(text: str) -> list[float]:
    """Return an embedding vector for `text` using the configured provider."""
    settings = get_settings()

    if settings.embedding_provider == "ollama":
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{settings.ollama_base_url}/api/embeddings",
                json={"model": settings.embedding_model, "prompt": text},
            )
            resp.raise_for_status()
            return resp.json()["embedding"]

    # "local" provider — synchronous under the hood, fine for our chunk sizes
    model = _get_local_model()
    return model.encode(text).tolist()
