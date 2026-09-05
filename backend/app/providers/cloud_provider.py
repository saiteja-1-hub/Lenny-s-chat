import logging
from typing import AsyncGenerator

import httpx

from app.config import get_settings
from app.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):
        settings = get_settings()

        key = api_key or settings.gemini_api_key

        if not key:
            raise ValueError(
                "GEMINI_API_KEY is not set. "
                "Add it to your environment variables."
            )

        self.api_key = key
        self.model = model or settings.gemini_model

        self.url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{self.model}:streamGenerateContent"
        )

    async def generate_response(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3,
    ) -> AsyncGenerator[str, None]:

        contents = []

        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            # Gemini uses "user" and "model"
            if role == "assistant":
                role = "model"

            contents.append(
                {
                    "role": role,
                    "parts": [
                        {
                            "text": content
                        }
                    ],
                }
            )

        payload = {
            "system_instruction": {
                "parts": [
                    {
                        "text": system_prompt
                    }
                ]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 4096,
            },
        }

        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:

                async with client.stream(
                    "POST",
                    self.url,
                    headers=headers,
                    params={
                        "alt": "sse"
                    },
                    json=payload,
                ) as response:

                    if response.status_code != 200:
                        body = await response.aread()

                        logger.error(
                            "Gemini API error %s: %s",
                            response.status_code,
                            body,
                        )

                        yield (
                            "[Error: Gemini API returned "
                            f"status {response.status_code}: "
                            f"{body.decode(errors='ignore')}]"
                        )
                        return

                    async for line in response.aiter_lines():

                        if not line:
                            continue

                        # Gemini SSE lines look like:
                        # data: {...}

                        if not line.startswith("data:"):
                            continue

                        data_text = line[5:].strip()

                        if not data_text:
                            continue

                        try:
                            import json

                            data = json.loads(data_text)

                            candidates = data.get(
                                "candidates",
                                []
                            )

                            if not candidates:
                                continue

                            candidate = candidates[0]

                            content = candidate.get(
                                "content",
                                {}
                            )

                            parts = content.get(
                                "parts",
                                []
                            )

                            for part in parts:
                                text = part.get(
                                    "text",
                                    ""
                                )

                                if text:
                                    yield text

                        except json.JSONDecodeError:
                            logger.warning(
                                "Could not parse Gemini SSE line: %s",
                                data_text,
                            )

        except httpx.ConnectError as exc:
            logger.error(
                "Could not connect to Gemini: %s",
                exc,
            )

            yield (
                "[Error: Could not reach Gemini API. "
                "Check your internet connection and "
                "GEMINI_API_KEY.]"
            )

        except httpx.HTTPError as exc:
            logger.error(
                "Gemini HTTP error: %s",
                exc,
            )

            yield (
                f"[Error: Gemini API request failed — {exc}]"
            )

        except Exception as exc:
            logger.exception(
                "Unexpected Gemini error"
            )

            yield (
                f"[Error: Gemini API call failed — {exc}]"
            )