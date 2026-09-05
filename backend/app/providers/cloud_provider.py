import logging
from typing import AsyncGenerator

import anthropic

from app.config import get_settings
from app.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class ClaudeProvider(BaseLLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        settings = get_settings()
        key = api_key or settings.anthropic_api_key
        if not key:
            raise ValueError(
                "ANTHROPIC_API_KEY is not set. Add it to your .env or choose the 'ollama' provider."
            )
        self.client = anthropic.AsyncAnthropic(api_key=key)
        self.model = model or settings.anthropic_model

    async def generate_response(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3,
    ) -> AsyncGenerator[str, None]:
        try:
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                temperature=temperature,
                messages=messages,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except anthropic.APIError as exc:
            logger.error("Anthropic API error: %s", exc)
            yield f"[Error: Anthropic API call failed — {exc}]"
