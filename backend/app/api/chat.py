import json
import logging

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, get_db
from app.models.db_models import Artifact, Message
from app.models.schemas import ChatRequest
from app.providers.base import BaseLLMProvider
from app.providers.cloud_provider import ClaudeProvider
from app.providers.ollama_provider import OllamaProvider
from app.rag.embeddings import get_embedding
from app.rag.retriever import TranscriptRetriever
from app.skills.artifact_generator import build_grounded_system_prompt, extract_artifacts
from app.skills.ship30_writer import build_ship30_prompt

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat"])


def get_provider(name: str) -> BaseLLMProvider:
    if name == "claude":
        return ClaudeProvider()
    return OllamaProvider()


def _sse(event_type: str, content) -> str:
    return f"data: {json.dumps({'type': event_type, 'content': content})}\n\n"


@router.post("")
async def stream_chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    # Persist the user's message immediately, using the request-scoped session.
    # This part finishes before the endpoint returns, so it's safe.
    user_message = Message(session_id=req.session_id, role="user", content=req.message)
    db.add(user_message)
    await db.commit()

    async def token_event_generator():
        # IMPORTANT: open a fresh DB session here rather than reusing the one injected
        # above. FastAPI closes yield-dependencies as soon as the endpoint function
        # returns, which happens right after we hand back the StreamingResponse below
        # — long before this generator actually finishes running. Reusing the closed
        # session causes "Internal Server Error" mid-stream.
        async with AsyncSessionLocal() as stream_db:
            retriever = TranscriptRetriever(stream_db, get_embedding)
            chunks = await retriever.retrieve_relevant_chunks(req.message)

            if req.mode == "ship30":
                system_prompt = (
                    "You are the Lenny Growth Assistant. "
                    "Ground every claim in the transcript context you're given."
                )
                user_content = build_ship30_prompt(req.message, chunks)
            else:
                system_prompt = build_grounded_system_prompt(chunks)
                user_content = req.message

            try:
                llm = get_provider(req.provider)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed to initialize LLM provider")
                yield _sse("status", "Retrieving transcripts...")
                yield _sse("sources", chunks)
                yield _sse("token", f"[Error: could not start '{req.provider}' provider — {exc}]")
                yield "data: [DONE]\n\n"
                return

            yield _sse("status", "Retrieving transcripts...")
            yield _sse("sources", chunks)

            full_response = ""
            try:
                async for token in llm.generate_response(
                    [{"role": "user", "content": user_content}], system_prompt
                ):
                    full_response += token
                    yield _sse("token", token)
            except Exception as exc:  # noqa: BLE001
                logger.exception("LLM generation failed")
                yield _sse("token", f"[Error generating response: {exc}]")

            visible_text, artifacts = extract_artifacts(full_response)

            assistant_message = Message(
                session_id=req.session_id,
                role="assistant",
                content=visible_text or full_response,
                sources=chunks,
            )
            stream_db.add(assistant_message)
            await stream_db.flush()

            for a in artifacts:
                stream_db.add(
                    Artifact(
                        message_id=assistant_message.id,
                        artifact_type=a.artifact_type,
                        title=a.title,
                        content=a.content,
                    )
                )
            await stream_db.commit()

            if artifacts:
                yield _sse(
                    "artifacts",
                    [
                        {"type": a.artifact_type, "title": a.title, "content": a.content}
                        for a in artifacts
                    ],
                )

            yield "data: [DONE]\n\n"

    return StreamingResponse(token_event_generator(), media_type="text/event-stream")