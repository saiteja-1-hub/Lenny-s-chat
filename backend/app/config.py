from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://postgres:password123@localhost:5432/lenny_assistant"

    # LLM providers
    default_provider: str = "ollama"  # "ollama" or "claude"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-6"

    # Embeddings
    embedding_provider: str = "ollama"  # "ollama" or "local"
    embedding_model: str = "nomic-embed-text"
    embedding_dim: int = 768  # 768 for nomic-embed-text, 384 for all-MiniLM-L6-v2

    # RAG
    top_k: int = 5
    similarity_threshold: float = 0.5

    # App
    cors_origins: list[str] = ["http://localhost:3000"]
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
