# Architecture Specification — The Lenny Growth Assistant

## 1. Architectural goals

The architecture is designed around five principles:

1. Retrieval before generation.
2. Provider independence.
3. Persistent and inspectable source metadata.
4. Secure artifact isolation.
5. Reproducible local deployment.

## 2. Logical architecture

```text
┌──────────────────────────────────────────────────────────┐
│                     Browser / Frontend                    │
│                                                          │
│  Session List   Chat Pane       Artifact Preview         │
│                    │                    │                │
│                    └──────────┬─────────┘                │
└───────────────────────────────┼──────────────────────────┘
                                │ HTTPS / SSE
                                ▼
┌──────────────────────────────────────────────────────────┐
│                     FastAPI Backend                       │
│                                                          │
│ API Routes → Session Service → RAG → LLM Provider       │
│                         │             │                  │
│                         ▼             ▼                  │
│                   PostgreSQL      Ollama / Cloud         │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
                 PostgreSQL + pgvector
                           ▲
                           │
                 Ingestion / Embeddings
                           ▲
                           │
                   Transcript Archive
```

## 3. Deployment architecture

Docker Compose contains:

```text
db
 └─ PostgreSQL 16 + pgvector

backend
 └─ FastAPI + Uvicorn

frontend
 └─ Next.js

ollama (optional)
 └─ Local LLM runtime
```

The provided baseline can connect the backend container to host Ollama through:

```text
host.docker.internal:11434
```

## 4. Backend modules

```text
backend/app/
├── main.py
├── config.py
├── database.py
├── models/
│   ├── db_models.py
│   └── schemas.py
├── providers/
│   ├── base.py
│   ├── ollama_provider.py
│   └── cloud_provider.py
├── rag/
│   ├── retriever.py
│   └── embeddings.py
├── skills/
│   ├── ship30_writer.py
│   └── artifact_generator.py
└── api/
    ├── sessions.py
    ├── chat.py
    └── health.py
```

### Responsibilities

**API layer**
- Request validation.
- HTTP/SSE responses.
- Authentication boundary if added later.

**RAG layer**
- Query embedding.
- Similarity search.
- Thresholding.
- Source metadata assembly.

**Provider layer**
- Provider-specific HTTP/API logic.
- Streaming.
- Provider error normalization.

**Skills layer**
- Ship 30 writing behavior.
- Artifact formatting.

**Persistence layer**
- Sessions.
- Messages.
- Artifacts.
- Transcript chunks.

## 5. Data model

### sessions

```text
id          UUID PK
title       TEXT
created_at  TIMESTAMP
updated_at  TIMESTAMP
```

### messages

```text
id          UUID PK
session_id  UUID FK
role        TEXT
content     TEXT
sources     JSONB
created_at  TIMESTAMP
```

### artifacts

```text
id            UUID PK
message_id    UUID FK
artifact_type TEXT  -- markdown | html
content       TEXT
```

### transcript_chunks

Recommended fields:

```text
id              BIGSERIAL PK
episode_title   TEXT
guest_name      TEXT
publication_date DATE
timestamp_ref   TEXT
chunk_text      TEXT
embedding       VECTOR
metadata        JSONB
created_at      TIMESTAMP
```

## 6. pgvector indexing

The embedding vector is stored using pgvector.

Conceptually:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

An HNSW index is recommended for approximate nearest-neighbor search.

For cosine similarity:

```sql
1 - (embedding <=> query_vector)
```

The application should:

1. Generate query vector.
2. Calculate similarity.
3. Filter below threshold.
4. Order descending.
5. Limit to top K.

Initial values:

```text
top_k = 5
threshold = 0.65
```

These are starting values, not universal constants. Evaluation data should be used to tune them.

## 7. Ingestion pipeline

```text
Transcript file
      │
      ▼
Parser
      │
      ▼
Metadata extraction
      │
      ▼
Chunker
500–800 tokens
~100 overlap
      │
      ▼
Embedding model
      │
      ▼
PostgreSQL / pgvector
      │
      ▼
HNSW index
```

The ingestion process must be idempotent or have a deterministic strategy for avoiding duplicate chunks.

## 8. Retrieval flow

```text
User question
     │
     ▼
Query embedding
     │
     ▼
pgvector similarity search
     │
     ├── No qualifying chunks ──► Evidence-gap response
     │
     ▼
Top 4–6 chunks
     │
     ▼
Grounded prompt
     │
     ▼
Selected LLM provider
     │
     ▼
Streaming response
     │
     ▼
Citation/source metadata
```

## 9. LLM provider contract

The application should depend on an abstract interface:

```python
class BaseLLMProvider:
    async def generate_response(
        self,
        messages,
        system_prompt,
        temperature=0.3
    ):
        ...
```

Implementations:

```text
BaseLLMProvider
 ├── OllamaProvider
 └── CloudProvider
```

The provider factory/router selects the implementation from configuration or request metadata.

Business logic must not depend directly on Ollama or Anthropic/OpenAI APIs.

## 10. Streaming protocol

The backend can use Server-Sent Events.

Example events:

```text
data: {"type":"status","content":"Retrieving transcripts..."}

data: {"type":"token","content":"Retention"}

data: {"type":"token","content":" is"}

data: {"type":"token","content":"..."}

data: [DONE]
```

The frontend accumulates token events into the active assistant message.

## 11. Artifact architecture

Artifact extraction:

```text
LLM response
      │
      ▼
Artifact parser
      │
      ├── Markdown ──► Markdown renderer
      │
      └── HTML ──────► Sanitizer ──► sandboxed iframe
```

Recommended iframe policy:

```html
sandbox="allow-scripts"
```

Do not grant `allow-same-origin` unless a separately reviewed security architecture requires it.

## 12. Security boundaries

### Browser

The browser must never receive:

- Database passwords
- LLM API keys
- Internal service credentials

### Artifact iframe

The artifact should be isolated from the parent origin.

Generated content should not be allowed to:

- Read application cookies.
- Read parent local storage.
- Access parent DOM.
- Make authenticated same-origin requests.

### Backend

Use:

- Pydantic validation.
- Timeouts.
- Structured logging.
- Exception handling.
- Secret management through environment variables.

## 13. Failure handling

### Database unavailable

Return a service-unavailable state and expose a degraded health result.

### Ollama unavailable

If configured, either:

- Return a clear provider error, or
- Fall back to the configured cloud provider.

Fallback behavior should be explicit rather than silent.

### Retrieval returns no evidence

Do not generate an apparently authoritative podcast-derived answer.

### LLM timeout

Stop the stream cleanly and return an actionable error.

## 14. Observability

Structured logs should include:

```text
request_id
session_id
provider
model
retrieval_count
top_similarity
latency_ms
error_type
```

Do not log secrets or complete sensitive prompts unnecessarily.

## 15. Scaling path

The MVP is a single Docker Compose deployment.

Future scale-out:

```text
Load Balancer
     │
     ├── Frontend instances
     │
     └── Backend instances
              │
       ┌──────┴──────┐
       ▼             ▼
 PostgreSQL       Redis/Queue
       │             │
       ▼             ▼
 pgvector       ingestion workers
```

Embedding and ingestion workloads can later move to asynchronous workers.

## 16. Architecture decisions

| Decision | Choice | Reason |
|---|---|---|
| API | FastAPI | Async Python ecosystem |
| DB | PostgreSQL | Relational persistence + mature ecosystem |
| Vector DB | pgvector | Avoid separate vector infrastructure |
| Index | HNSW | Fast ANN search |
| Local LLM | Ollama | Simple local runtime |
| Frontend | Next.js | Strong React application structure |
| Styling | Tailwind | Rapid consistent UI development |
| Streaming | SSE | Simple server-to-browser streaming |
| Artifact isolation | iframe sandbox | Strong browser security boundary |
