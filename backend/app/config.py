from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # ============================================================
    # DATABASE
    # ============================================================

    database_url: str = (
        "postgresql+asyncpg://postgres:password123@localhost:5432/lenny_assistant"
    )

    # ============================================================
    # DEFAULT LLM PROVIDER
    # ============================================================

    # Production: Gemini
    # Local development: change to "ollama" if needed
    default_provider: str = "gemini"

    # ============================================================
    # GEMINI
    # ============================================================

    gemini_api_key: str | None = None

    # Gemini model used for chat generation
    gemini_model: str = "gemini-2.5-flash"

    # ============================================================
    # OLLAMA
    # ============================================================

    # Used for local development only
    ollama_base_url: str = "http://localhost:11434"

    ollama_model: str = "llama3.1:8b"

    # ============================================================
    # EMBEDDINGS
    # ============================================================

    # Production:
    # Gemini embeddings
    #
    # Local development:
    # Ollama embeddings can be used by changing this to "ollama"
    embedding_provider: str = "gemini"

    # Gemini embedding model
    embedding_model: str = "gemini-embedding-001"

    # IMPORTANT:
    # Your PostgreSQL pgvector column is Vector(768),
    # so this must remain 768.
    embedding_dim: int = 768

    # ============================================================
    # RAG / RETRIEVAL
    # ============================================================

    # Number of transcript chunks retrieved
    top_k: int = 5

    # Minimum similarity score required for retrieved chunks
    similarity_threshold: float = 0.5

    # ============================================================
    # CORS
    # ============================================================

    cors_origins: list[str] = [
        "http://localhost:3000",
        "https://chat-lenny-ai.onrender.com",
    ]

    # ============================================================
    # LOGGING
    # ============================================================

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()