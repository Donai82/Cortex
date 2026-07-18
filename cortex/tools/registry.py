from cortex.core.exceptions import NotFoundError

from .interface import Tool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise NotFoundError(f"Tool {name} not found")
        return self._tools[name]

    def list(self) -> list[Tool]:
        return list(self._tools.values())
