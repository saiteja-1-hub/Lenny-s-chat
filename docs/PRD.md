# Product Requirements Document — The Lenny Growth Assistant

## 1. Product summary

The Lenny Growth Assistant is a RAG-powered knowledge assistant for product managers and growth leaders. It makes operational lessons contained in Lenny's Podcast transcripts accessible through natural-language questions instead of requiring users to search or listen through hundreds of hours of content.

The product prioritizes grounded answers, transparent citations, practical outputs, and a demonstrable local inference workflow.

## 2. Problem

Product and growth practitioners frequently need tactical answers about:

- Product strategy
- Growth loops
- Retention
- Product-market fit
- Experimentation
- Pricing
- Team building
- Go-to-market
- Customer research

The knowledge exists across a large transcript archive, but finding the right passage manually is slow. A generic LLM may answer fluently while mixing outside knowledge with podcast content.

The product solves both problems through retrieval-first generation.

## 3. Primary persona

### Growth/Product PM

A product or growth manager who wants a fast, evidence-backed answer to a practical problem without listening to the entire podcast archive.

### Secondary personas

- Startup founders
- Growth leads
- Product designers
- Product operations teams
- Researchers studying product/growth practices

## 4. Goals

### Must achieve

1. Provide grounded answers from transcript evidence.
2. Show useful source attribution.
3. Handle insufficient evidence explicitly.
4. Generate a structured long-form essay from retrieved knowledge.
5. Provide an in-app artifact preview.
6. Allow local/cloud model switching.
7. Be reproducible with Docker Compose.

### Non-goals

- Replacing professional judgment.
- Treating the assistant as a general-purpose web search engine.
- Claiming that an idea came from a podcast when it was not retrieved.
- Executing arbitrary generated code on the host machine.
- Building a general social network or content publishing platform.

## 5. Core user stories

### Grounded Q&A

As a growth PM, I want to ask a natural-language question so that I can receive an actionable answer grounded in podcast transcripts.

### Source inspection

As a user, I want to see the episode/guest/topic associated with an answer so that I can evaluate the evidence.

### Evidence gap

As a user, I want the system to say when it lacks sufficient transcript evidence so that I do not mistake hallucination for source knowledge.

### Ship 30 mode

As a user, I want to turn retrieved insights into a structured essay so that I can use the knowledge as a reusable content artifact.

### Artifact preview

As a user, I want generated Markdown or HTML to appear beside the conversation so that I can inspect the output without leaving the app.

### Model switching

As a demo/operator, I want to switch between Ollama and a cloud provider without changing application logic.

## 6. Functional requirements

### FR-1 — Sessions

The system shall create persistent chat sessions.

Each session contains:

- UUID
- Title
- Created timestamp
- Updated timestamp

### FR-2 — Messages

Each message shall contain:

- ID
- Session ID
- Role
- Content
- Source metadata
- Created timestamp

### FR-3 — Retrieval

The system shall:

- Embed incoming queries.
- Search pgvector.
- Return top K relevant chunks.
- Apply a configurable similarity threshold.
- Preserve episode and guest metadata.

Target configuration:

```text
K = 4–6
Chunk size = 500–800 tokens
Overlap = ~100 tokens
```

### FR-4 — Grounded generation

The model prompt shall instruct the LLM to:

- Use retrieved context as the factual source.
- Attribute claims.
- Avoid inventing transcript content.
- State when evidence is insufficient.

### FR-5 — Provider abstraction

A common interface shall expose asynchronous generation/streaming.

Initial implementations:

- Ollama
- Anthropic or OpenAI

Provider selection shall be runtime configurable.

### FR-6 — Ship 30 for 30

The system shall generate approximately 1,250 words with:

- Hook
- Headings
- Short paragraphs
- Bold anchors
- Actionable conclusion
- Source attribution

### FR-7 — Artifacts

The system shall detect artifact blocks and support:

- Markdown rendering
- HTML/CSS preview
- Collapsible right pane
- Sandboxed execution

### FR-8 — Health

The health endpoint shall report relevant state for:

- PostgreSQL
- Vector index/data availability
- Ollama
- Application readiness

## 7. Non-functional requirements

### Performance

Target local inference first-token latency: < 4 seconds in the required demo environment.

### Reliability

- Graceful provider failures
- Database health checks
- Request timeouts
- Structured logs
- Global exception handling

### Security

- No secrets in source control.
- Validate API input.
- Sanitize artifact content.
- Sandbox HTML.
- Do not use `allow-same-origin` for generated artifact iframe content.
- Do not expose server-side credentials to the browser.

### Maintainability

RAG, providers, API routes, persistence, and frontend rendering should remain modular.

## 8. Success metrics

| Metric | Target |
|---|---:|
| Retrieval citation accuracy | >= 90% |
| Local first-token latency | < 4s |
| Known XSS vulnerabilities in artifact flow | 0 |
| Docker startup reproducibility | 100% on supported environment |
| Provider switching | No core-code modification |

## 9. Product risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Poor retrieval | High | Better chunking, metadata, threshold tuning |
| Local 7B/8B reasoning limitations | Medium | Strong prompts, retrieval constraints, cloud fallback |
| Hallucinated citations | High | Generate citations from retrieved metadata |
| Unsafe HTML | High | DOMPurify + sandboxed iframe |
| Slow local inference | Medium | Smaller model, GPU acceleration, streaming |
| Bad transcript parsing | High | Ingestion validation and fixture tests |
| Vector index misconfiguration | High | Startup checks and integration tests |

## 10. Acceptance criteria

The MVP is complete when:

- Docker Compose starts DB/backend/frontend.
- Transcript chunks can be indexed.
- A question retrieves relevant chunks.
- The response includes source attribution.
- Unsupported questions receive an evidence-gap response.
- Ollama can generate a streamed answer.
- A cloud provider can be selected through the same interface.
- Ship 30 mode creates a structured essay.
- Artifact preview renders safely.
- Tests cover retrieval and provider switching.
- Documentation is sufficient for a fresh developer to run the project.

## 11. Trade-offs

### Local model vs cloud

Local Ollama:

- Lower ongoing API cost.
- Better privacy/control.
- Works for the evaluation demo.
- Requires local hardware and model downloads.
- Usually has weaker reasoning than larger hosted models.

Cloud:

- Stronger reasoning and generation quality.
- Easier scaling.
- Requires credentials and network access.
- Adds usage cost and provider dependency.

The architecture therefore treats the LLM as a replaceable infrastructure component.

## 12. Future enhancements

- Hybrid keyword + vector retrieval.
- Reranking.
- Conversation-aware retrieval.
- Citation verification.
- Evaluation dashboard.
- User feedback loop.
- Background ingestion jobs.
- Multi-tenant authentication.
- Export to Markdown/PDF.
