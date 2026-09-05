# The Lenny Growth Assistant

A full-stack, enterprise-oriented Retrieval-Augmented Generation (RAG) application that turns Lenny's Podcast transcripts into a searchable knowledge assistant for product managers and growth leaders.

## What it does

- Answers product and growth questions using retrieved podcast transcript context.
- Attributes answers to episodes, guests, timestamps, or topics.
- Explicitly acknowledges when the transcript archive does not contain enough relevant evidence.
- Generates approximately 1,250-word essays using a Ship 30 for 30-inspired structure.
- Displays generated Markdown and HTML/CSS artifacts in a side-by-side preview.
- Supports local Ollama inference and a cloud LLM provider through one provider abstraction.
- Uses PostgreSQL + pgvector for persistent transcript/vector storage.
- Streams responses through FastAPI.
- Runs locally through Docker Compose.

## Architecture at a glance

```text
                    ┌─────────────────────────────┐
                    │       Next.js Frontend      │
                    │ Chat │ Sessions │ Artifacts │
                    └──────────────┬──────────────┘
                                   │ HTTP / SSE
                                   ▼
                    ┌─────────────────────────────┐
                    │       FastAPI Backend       │
                    │ API │ RAG │ Skills │ Router │
                    └───────┬──────────┬──────────┘
                            │          │
                  similarity search    │ LLM
                            │          │
                            ▼          ▼
                 ┌────────────────┐  ┌───────────────┐
                 │ PostgreSQL +   │  │ Ollama / Cloud│
                 │ pgvector       │  │ LLM Provider  │
                 └────────────────┘  └───────────────┘
```

## Requirements

- 4+ CPU cores
- 16 GB RAM recommended
- 15 GB+ free disk space
- Python 3.11+
- Node.js 18/20 LTS
- Docker 24+
- Docker Compose
- Ollama for the local-model demo

## Quick start

1. Copy the environment template:

```bash
cp .env.example .env
```

On Windows, create `.env` manually from `.env.example`.

2. Start the application:

```bash
docker-compose up --build
```

3. Open:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Health: `http://localhost:8000/api/health`

4. If Ollama is running on the host:

```bash
ollama pull llama3.2:3b
```

Then use `ollama` as the default provider.

## Knowledge ingestion

Download or place the transcript archive in the configured source directory, then run:

```bash
python backend/scripts/download_transcripts.py
python backend/scripts/ingest.py
```

The ingestion pipeline:

1. Parses Markdown/TXT transcripts.
2. Extracts episode and guest metadata.
3. Splits transcripts into approximately 500–800-token chunks.
4. Uses approximately 100-token overlap.
5. Generates embeddings.
6. Stores chunks and vectors in PostgreSQL.
7. Builds/uses an HNSW vector index.

## RAG behavior

For every user question:

1. Embed the question.
2. Retrieve the top 4–6 transcript chunks.
3. Apply a similarity threshold.
4. Build a grounded prompt containing only retrieved evidence.
5. Generate a cited answer.
6. Refuse to invent podcast-derived facts when evidence is insufficient.

Example citation:

```text
[Episode: Brian Balfour, Retention Strategy]
```

## Ship 30 for 30 mode

The writing mode produces an approximately 1,250-word article with:

- A strong curiosity-driven hook.
- Short paragraphs.
- Markdown headings.
- Bold anchors.
- Practical examples.
- A concrete framework/checklist.
- Source attribution.

## Artifact viewer

Generated artifacts can be:

- Markdown
- HTML/CSS

HTML is displayed using a sandboxed iframe. The intended security posture is:

```html
sandbox="allow-scripts"
```

`allow-same-origin` is intentionally omitted so the artifact cannot share the normal origin with the parent application.

Sanitization should be applied before rendering, and artifact functionality must not expose application cookies, local storage, parent DOM, or authenticated APIs.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/sessions` | Create a chat session |
| GET | `/api/sessions/{session_id}` | Retrieve session history |
| POST | `/api/chat` | Stream a grounded response |
| GET | `/api/health` | Check service health |

## Testing

```bash
pytest backend/tests
```

Important test areas:

- Vector similarity retrieval.
- Similarity threshold behavior.
- Empty/out-of-domain questions.
- Provider switching.
- API streaming.
- Session persistence.
- Artifact parsing/safety.

## Environment variables

Typical configuration:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password123@db:5432/lenny_assistant
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.2:3b
DEFAULT_LLM_PROVIDER=ollama
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
```

Never commit real API keys or production credentials.

## Success targets

- Retrieval citation accuracy: >= 90%
- Local first-token latency: < 4 seconds under the target demo environment
- Artifact rendering: 0 known XSS vulnerabilities in security testing
- Reproducible startup using Docker Compose
- Provider switching without changes to RAG/business logic

## Documentation

- `docs/PRD.md` — product requirements and acceptance criteria
- `docs/architecture.md` — system architecture and data contracts
- `docs/design.md` — UI/UX and interaction specification
- `agent_transcripts/01_initial_scaffolding.md` — initial implementation record
- `agent_transcripts/02_debugging_pgvector_indexing.md` — debugging record

## Demo checklist

The 2–3 minute demo should show:

1. Starting the stack.
2. Asking a transcript-grounded question.
3. Showing source attribution.
4. Switching to local Ollama.
5. Generating a Ship 30 for 30 essay.
6. Opening an artifact in the right pane.
7. Demonstrating the health endpoint.
8. Explaining local-vs-cloud trade-offs.
