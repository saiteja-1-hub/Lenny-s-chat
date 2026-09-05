from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    # ============================================================
    # Database
    # ============================================================

    database_url: str = (
        "postgresql+asyncpg://postgres:password123@localhost:5432/"
        "lenny_assistant"
    )

    # ============================================================
    # LLM Providers
    # ============================================================

    # Production LLM
    default_provider: str = "claude"

    # Ollama - local development only
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    # Claude
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-6"

    # ============================================================
    # Gemini
    # ============================================================

    gemini_api_key: str | None = None

    # ============================================================
    # Embeddings
    # ============================================================

    # Production embedding provider
    embedding_provider: str = "gemini"

    # Gemini embedding model
    embedding_model: str = "gemini-embedding-001"

    # IMPORTANT:
    # PostgreSQL currently uses Vector(768)
    embedding_dim: int = 768

    # ============================================================
    # RAG
    # ============================================================

    top_k: int = 5

    similarity_threshold: float = 0.5

    # ============================================================
    # Application
    # ============================================================

    cors_origins: list[str] = [
        "http://localhost:3000"
    ]

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()