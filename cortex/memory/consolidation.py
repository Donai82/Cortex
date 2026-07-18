from typing import Protocol

from .models import MemoryRecord, SemanticFact


class Consolidator(Protocol):
    async def consolidate(self, records: list[MemoryRecord]) -> list[SemanticFact]: ...


class ConsolidationEngine:
    async def consolidate(self, records: list[MemoryRecord]) -> list[SemanticFact]:
        return []
