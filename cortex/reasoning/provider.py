from typing import Protocol

from .models import ReasoningRequest, ReasoningResponse


class ReasoningProvider(Protocol):
    async def generate(self, request: ReasoningRequest) -> ReasoningResponse: ...
