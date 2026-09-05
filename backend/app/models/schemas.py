import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


# ---- Sessions ----
class SessionCreate(BaseModel):
    title: str = Field(default="New Chat")


class SessionOut(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---- Messages ----
class SourceRef(BaseModel):
    episode: str
    guest: str
    timestamp: str | None = None
    score: float


class ArtifactOut(BaseModel):
    id: uuid.UUID
    artifact_type: Literal["markdown", "html"]
    title: str
    content: str

    class Config:
        from_attributes = True


class MessageOut(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    sources: list[dict[str, Any]] | None = None
    created_at: datetime
    artifacts: list[ArtifactOut] = []

    class Config:
        from_attributes = True


class SessionDetailOut(SessionOut):
    messages: list[MessageOut] = []


# ---- Chat ----
class ChatRequest(BaseModel):
    session_id: uuid.UUID
    message: str
    mode: Literal["default", "ship30"] = "default"
    provider: Literal["ollama", "claude"] = "ollama"


# ---- Health ----
class HealthOut(BaseModel):
    status: Literal["ok", "degraded"]
    database: bool
    ollama: bool
    vector_index_rows: int
