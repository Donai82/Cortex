from .models import SideEffect, ToolResult


class EchoTool:
    name = "echo"
    description = "Returns its input"
    side_effect = SideEffect.NONE
    required_permissions: list[str] = []

    async def execute(self, input: str) -> ToolResult:
        return ToolResult(success=True, output=input)
