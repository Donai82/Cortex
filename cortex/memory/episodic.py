from uuid import UUID

from .models import MemoryRecord


class EpisodicMemory:
    def __init__(self) -> None:
        self._records: list[MemoryRecord] = []

    async def add(self, record: MemoryRecord) -> None:
        self._records.append(record)

    async def for_run(self, run_id: UUID) -> list[MemoryRecord]:
        return [r for r in self._records if r.source_run_id == run_id]

    async def all(self) -> list[MemoryRecord]:
        return list(self._records)
