from typing import Protocol

from .models import SideEffect, ToolResult


class Tool(Protocol):
    name: str
    description: str
    side_effect: SideEffect
    required_permissions: list[str]

    async def execute(self, input: str) -> ToolResult: ...


class ToolResolver(Protocol):
    def get(self, name: str) -> Tool: ...
