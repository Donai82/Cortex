import asyncio
import json
import time
from typing import Any

import httpx

from cortex.core.config import Settings
from cortex.core.exceptions import (
    ProviderAuthenticationError,
    ProviderFailureError,
    ProviderHTTPError,
    ProviderMalformedResponseError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)

from .models import ReasoningRequest, ReasoningResponse


class OpenRouterReasoningProvider:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self.client = client or httpx.AsyncClient(timeout=settings.openrouter_timeout_seconds)

    async def generate(self, request: ReasoningRequest) -> ReasoningResponse:
        if not self.settings.openrouter_api_key:
            raise ProviderAuthenticationError("OpenRouter API key is not configured")

        model = self.settings.resolve_model(request.role)
        payload: dict[str, Any] = {
            "model": model,
            "messages": [message.model_dump() for message in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_output_tokens,
        }
        if request.response_schema is not None:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": "cortex_response", "schema": request.response_schema},
            }

        started = time.perf_counter()
        for attempt in range(self.settings.openrouter_max_retries + 1):
            try:
                response = await self.client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.settings.openrouter_api_key}"},
                    json=payload,
                    timeout=self.settings.openrouter_timeout_seconds,
                )
            except httpx.TimeoutException as exc:
                if attempt < self.settings.openrouter_max_retries:
                    await self._backoff(attempt)
                    continue
                raise ProviderTimeoutError("OpenRouter request timed out") from exc
            except httpx.HTTPError as exc:
                if attempt < self.settings.openrouter_max_retries:
                    await self._backoff(attempt)
                    continue
                raise ProviderFailureError("OpenRouter request failed") from exc

            if response.status_code == 401 or response.status_code == 403:
                raise ProviderAuthenticationError("OpenRouter authentication failed")
            if response.status_code == 429:
                if attempt < self.settings.openrouter_max_retries:
                    await self._backoff(attempt)
                    continue
                raise ProviderRateLimitError("OpenRouter rate limit exceeded")
            if response.status_code >= 500 and attempt < self.settings.openrouter_max_retries:
                await self._backoff(attempt)
                continue
            if response.is_error:
                raise ProviderHTTPError(f"OpenRouter returned HTTP {response.status_code}")

            try:
                data = response.json()
                if not isinstance(data, dict):
                    raise TypeError("response is not an object")
                choice = data["choices"][0]
                message = choice["message"]
                text = message["content"]
                if not isinstance(text, str):
                    raise TypeError("content is not text")
            except (ValueError, TypeError, KeyError, IndexError) as exc:
                raise ProviderMalformedResponseError("OpenRouter response was invalid") from exc

            structured = None
            if request.response_schema is not None:
                try:
                    parsed = json.loads(text)
                    if not isinstance(parsed, dict):
                        raise TypeError("structured content is not an object")
                    structured = parsed
                except (json.JSONDecodeError, TypeError) as exc:
                    raise ProviderMalformedResponseError(
                        "OpenRouter structured response was invalid JSON"
                    ) from exc

            usage = data.get("usage") or {}
            if not isinstance(usage, dict):
                raise ProviderMalformedResponseError("OpenRouter usage metadata was invalid")
            cost = usage.get("cost", data.get("cost", 0.0))
            try:
                estimated_cost = float(cost or 0.0)
            except (TypeError, ValueError):
                estimated_cost = 0.0
            try:
                input_tokens = int(usage.get("prompt_tokens", usage.get("input_tokens", 0)) or 0)
                output_tokens = int(
                    usage.get("completion_tokens", usage.get("output_tokens", 0)) or 0
                )
            except (TypeError, ValueError) as exc:
                raise ProviderMalformedResponseError(
                    "OpenRouter token usage metadata was invalid"
                ) from exc
            return ReasoningResponse(
                structured_content=structured,
                raw_text=text,
                model_name=data.get("model") or model,
                provider_name="openrouter",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost=estimated_cost,
                latency_ms=(time.perf_counter() - started) * 1000,
                finish_reason=choice.get("finish_reason") or "stop",
            )

        raise ProviderFailureError("OpenRouter request exhausted retries")

    async def _backoff(self, attempt: int) -> None:
        await asyncio.sleep(self.settings.openrouter_backoff_seconds * (2**attempt))
