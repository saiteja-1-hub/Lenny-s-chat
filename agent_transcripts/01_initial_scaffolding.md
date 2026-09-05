# Agent Transcript 01 — Initial Scaffolding

## Objective

Establish the initial full-stack structure for The Lenny Growth Assistant before implementing retrieval and provider-specific behavior.

## Initial decisions

- Backend: FastAPI + Python 3.11+
- Frontend: Next.js + TypeScript + Tailwind CSS
- Database: PostgreSQL 16 with pgvector
- Local inference: Ollama
- Cloud inference: replaceable provider interface
- Streaming: Server-Sent Events
- Deployment: Docker Compose

## Initial directory plan

```text
lenny-growth-assistant/
├── docs/
├── agent_transcripts/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── providers/
│   │   ├── rag/
│   │   └── skills/
│   ├── scripts/
│   └── tests/
└── frontend/
    └── src/
```

## Backend scaffold

The backend responsibilities were separated into:

1. API routes.
2. Database access.
3. Pydantic schemas.
4. Provider implementations.
5. Retrieval/embedding logic.
6. Content-generation skills.

The provider abstraction was deliberately introduced before wiring Ollama so that the rest of the application would not depend on a single model vendor.

## API scaffold

Initial routes:

```text
POST /api/sessions
GET  /api/sessions/{session_id}
POST /api/chat
GET  /api/health
```

The chat endpoint was designed around SSE to support token streaming.

## Frontend scaffold

The frontend was organized around the primary workspace:

```text
Sidebar | Chat | Artifact
```

The artifact area was made collapsible so that the application could support both normal Q&A and generated content previews.

## Initial database model

The first persistence layer included:

- sessions
- messages
- artifacts
- transcript chunks

The transcript chunk model was designed to retain enough source metadata to generate human-readable citations.

## Initial risks identified

### Risk 1 — Local model performance

A 7B/8B model may not match cloud-model reasoning quality.

Decision: keep prompts concise, retrieve high-quality context, and allow cloud-provider substitution.

### Risk 2 — Hallucinated source attribution

Decision: citations should be derived from retrieved chunk metadata rather than invented by the model where possible.

### Risk 3 — Artifact security

Decision: generated HTML must be isolated in a sandboxed iframe and sanitized before rendering.

## Scaffold completion criteria

The scaffold is considered complete when:

- Backend starts.
- Frontend starts.
- Database starts.
- Health endpoint responds.
- Provider interface can be instantiated.
- Frontend can establish an API connection.
- Docker Compose can orchestrate the core services.

## Next implementation phase

The next phase is transcript ingestion and pgvector indexing. The highest-risk area is ensuring the database extension, vector column type, embedding dimensions, and index configuration all agree.
