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

    # "ollama" for local development
    # "claude" for production
    default_provider: str = "claude"

    # Ollama - mainly for local development
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    # Anthropic / Claude
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-6"

    # OpenAI
    # Used for embeddings in production
    openai_api_key: str | None = None

    # ============================================================
    # Embeddings
    # ============================================================

    # "ollama" for local development
    # "openai" for production
    embedding_provider: str = "openai"

    # OpenAI embedding model
    embedding_model: str = "text-embedding-3-small"

    # IMPORTANT:
    # Your PostgreSQL pgvector column is currently Vector(768)
    embedding_dim: int = 768

    # ============================================================
    # RAG
    # ============================================================

    # Number of chunks returned by similarity search
    top_k: int = 5

    # Minimum similarity required for a chunk
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