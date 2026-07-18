import asyncio
from collections import deque
from collections.abc import Iterable

from cortex.core.exceptions import ProviderFailureError, ProviderMalformedResponseError

from .models import ReasoningRequest, ReasoningResponse


class FakeReasoningProvider:
    def __init__(
        self,
        responses: list[ReasoningResponse] | None = None,
        latency: float = 0.0,
        fail: bool = False,
        malformed: bool = False,
        input_tokens: int = 0,
        output_tokens: int = 2,
        estimated_cost: float = 0.0,
        model_name: str = "fake",
    ) -> None:
        self.responses = deque(responses or [])
        self.latency = latency
        self.fail = fail
        self.malformed = malformed
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.estimated_cost = estimated_cost
        self.model_name = model_name
        self.requests: list[ReasoningRequest] = []

    def queue_response(self, response: ReasoningResponse) -> None:
        self.responses.append(response)

    def queue_responses(self, responses: Iterable[ReasoningResponse]) -> None:
        self.responses.extend(responses)

    async def generate(self, request: ReasoningRequest) -> ReasoningResponse:
        self.requests.append(request)
        if self.latency:
            await asyncio.sleep(self.latency)
        if self.fail:
            raise ProviderFailureError("fake provider failure")
        if self.malformed:
            raise ProviderMalformedResponseError("malformed fake response")
        if self.responses:
            return self.responses.popleft()
        text = "deterministic decision"
        return ReasoningResponse(
            raw_text=text,
            structured_content={"decision": text},
            model_name=self.model_name,
            provider_name="fake",
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            estimated_cost=self.estimated_cost,
        )
