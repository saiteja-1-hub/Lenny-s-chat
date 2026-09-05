import json
import logging

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, get_db
from app.models.db_models import Artifact, Message
from app.models.schemas import ChatRequest
from app.providers.base import BaseLLMProvider
from app.providers.cloud_provider import GeminiProvider
from app.providers.ollama_provider import OllamaProvider
from app.rag.embeddings import get_embedding
from app.rag.retriever import TranscriptRetriever
from app.skills.artifact_generator import (
    build_grounded_system_prompt,
    extract_artifacts,
)
from app.skills.ship30_writer import build_ship30_prompt

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


def get_provider(name: str) -> BaseLLMProvider:
    """
    Return the requested LLM provider.

    Production:
        gemini

    Local development:
        ollama
    """

    if name == "gemini":
        return GeminiProvider()

    if name == "ollama":
        return OllamaProvider()

    raise ValueError(
        f"Unsupported provider '{name}'. "
        "Use 'gemini' or 'ollama'."
    )


def _sse(event_type: str, content) -> str:
    return (
        f"data: {json.dumps({'type': event_type, 'content': content})}"
        "\n\n"
    )


@router.post("")
async def stream_chat(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    # ------------------------------------------------------------
    # Save user's message
    # ------------------------------------------------------------

    user_message = Message(
        session_id=req.session_id,
        role="user",
        content=req.message,
    )

    db.add(user_message)

    await db.commit()

    # ------------------------------------------------------------
    # Streaming generator
    # ------------------------------------------------------------

    async def token_event_generator():

        # Open a fresh DB session for the streaming operation.
        async with AsyncSessionLocal() as stream_db:

            # ----------------------------------------------------
            # RAG retrieval
            # ----------------------------------------------------

            retriever = TranscriptRetriever(
                stream_db,
                get_embedding,
            )

            try:
                chunks = await retriever.retrieve_relevant_chunks(
                    req.message
                )

            except Exception as exc:
                logger.exception(
                    "RAG retrieval failed"
                )

                yield _sse(
                    "token",
                    f"[Error retrieving transcripts: {exc}]",
                )

                yield "data: [DONE]\n\n"
                return

            # ----------------------------------------------------
            # Build prompt
            # ----------------------------------------------------

            if req.mode == "ship30":

                system_prompt = (
                    "You are the Lenny Growth Assistant. "
                    "Ground every claim in the transcript context "
                    "you're given."
                )

                user_content = build_ship30_prompt(
                    req.message,
                    chunks,
                )

            else:

                system_prompt = build_grounded_system_prompt(
                    chunks
                )

                user_content = req.message

            # ----------------------------------------------------
            # Initialize provider
            # ----------------------------------------------------

            try:

                llm = get_provider(req.provider)

            except Exception as exc:

                logger.exception(
                    "Failed to initialize LLM provider"
                )

                yield _sse(
                    "status",
                    "Retrieving transcripts...",
                )

                yield _sse(
                    "sources",
                    chunks,
                )

                yield _sse(
                    "token",
                    (
                        f"[Error: could not start "
                        f"'{req.provider}' provider — {exc}]"
                    ),
                )

                yield "data: [DONE]\n\n"

                return

            # ----------------------------------------------------
            # Send status and sources
            # ----------------------------------------------------

            yield _sse(
                "status",
                "Retrieving transcripts...",
            )

            yield _sse(
                "sources",
                chunks,
            )

            # ----------------------------------------------------
            # Generate response
            # ----------------------------------------------------

            full_response = ""

            try:

                async for token in llm.generate_response(
                    [
                        {
                            "role": "user",
                            "content": user_content,
                        }
                    ],
                    system_prompt,
                ):

                    full_response += token

                    yield _sse(
                        "token",
                        token,
                    )

            except Exception as exc:

                logger.exception(
                    "LLM generation failed"
                )

                yield _sse(
                    "token",
                    f"[Error generating response: {exc}]",
                )

            # ----------------------------------------------------
            # Extract artifacts
            # ----------------------------------------------------

            visible_text, artifacts = extract_artifacts(
                full_response
            )

            # ----------------------------------------------------
            # Save assistant message
            # ----------------------------------------------------

            assistant_message = Message(
                session_id=req.session_id,
                role="assistant",
                content=visible_text or full_response,
                sources=chunks,
            )

            stream_db.add(
                assistant_message
            )

            await stream_db.flush()

            # ----------------------------------------------------
            # Save artifacts
            # ----------------------------------------------------

            for artifact in artifacts:

                stream_db.add(
                    Artifact(
                        message_id=assistant_message.id,
                        artifact_type=artifact.artifact_type,
                        title=artifact.title,
                        content=artifact.content,
                    )
                )

            await stream_db.commit()

            # ----------------------------------------------------
            # Send artifacts
            # ----------------------------------------------------

            if artifacts:

                yield _sse(
                    "artifacts",
                    [
                        {
                            "type": artifact.artifact_type,
                            "title": artifact.title,
                            "content": artifact.content,
                        }
                        for artifact in artifacts
                    ],
                )

            # ----------------------------------------------------
            # Finish SSE stream
            # ----------------------------------------------------

            yield "data: [DONE]\n\n"

    return StreamingResponse(
        token_event_generator(),
        media_type="text/event-stream",
    )