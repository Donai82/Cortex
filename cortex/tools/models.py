from enum import StrEnum

from pydantic import BaseModel


class SideEffect(StrEnum):
    NONE = "none"
    READ = "read"
    WRITE = "write"
    EXTERNAL_COMMUNICATION = "external_communication"
    DESTRUCTIVE = "destructive"


class ToolResult(BaseModel):
    success: bool
    output: str
    error: str | None = None
