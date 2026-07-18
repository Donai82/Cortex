import json

import httpx
import pytest

from cortex.core.config import Settings
from cortex.core.exceptions import (
    ProviderAuthenticationError,
    ProviderFailureError,
    ProviderMalformedResponseError,
    ProviderRateLimitError,
)
from cortex.reasoning import FakeReasoningProvider, OpenRouterReasoningProvider
from cortex.reasoning.models import Message, ReasoningRequest, ReasoningResponse


def request(**kwargs: object) -> ReasoningRequest:
    return ReasoningRequest(messages=[Message(role="user", content="hello")], **kwargs)


@pytest.mark.asyncio
async def test_fake_queues_records_and_returns_metadata() -> None:
    response = ReasoningResponse(raw_text="queued", model_name="test", provider_name="fake")
    provider = FakeReasoningProvider(
        responses=[response], input_tokens=3, output_tokens=4, estimated_cost=0.01
    )

    result = await provider.generate(request())

    assert result.raw_text == "queued"
    assert result is response
    assert provider.requests == [request()]


@pytest.mark.asyncio
async def test_fake_failure_and_malformed_response_are_typed() -> None:
    with pytest.raises(ProviderFailureError):
        await FakeReasoningProvider(fail=True).generate(request())
    with pytest.raises(ProviderMalformedResponseError):
        await FakeReasoningProvider(malformed=True).generate(request())


def mocked_client(handler: httpx.MockTransport) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=handler)


@pytest.mark.asyncio
async def test_openrouter_parses_structured_content_and_usage() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "model": "example/model",
                "choices": [
                    {"message": {"content": json.dumps({"answer": "yes"})}, "finish_reason": "stop"}
                ],
                "usage": {"prompt_tokens": 5, "completion_tokens": 2, "cost": 0.003},
            },
            request=request,
        )

    settings = Settings(
        openrouter_api_key="secret", model_reasoning="example/model", openrouter_backoff_seconds=0
    )
    provider = OpenRouterReasoningProvider(settings, mocked_client(httpx.MockTransport(handler)))
    result = await provider.generate(request(response_schema={"type": "object"}))

    assert result.structured_content == {"answer": "yes"}
    assert result.input_tokens == 5
    assert result.output_tokens == 2
    assert result.estimated_cost == 0.003
    assert result.latency_ms >= 0


@pytest.mark.asyncio
async def test_openrouter_retries_rate_limit_without_network() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(429, request=request)

    settings = Settings(
        openrouter_api_key="secret", openrouter_max_retries=1, openrouter_backoff_seconds=0
    )
    provider = OpenRouterReasoningProvider(settings, mocked_client(httpx.MockTransport(handler)))

    with pytest.raises(ProviderRateLimitError):
        await provider.generate(request())
    assert calls == 2


@pytest.mark.asyncio
async def test_openrouter_rejects_invalid_structured_response_and_missing_key() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": []}, request=request)

    provider = OpenRouterReasoningProvider(
        Settings(openrouter_api_key="secret"), mocked_client(httpx.MockTransport(handler))
    )
    with pytest.raises(ProviderMalformedResponseError):
        await provider.generate(request(response_schema={"type": "object"}))
    with pytest.raises(ProviderAuthenticationError):
        await OpenRouterReasoningProvider(Settings()).generate(request())
