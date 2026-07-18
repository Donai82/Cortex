from uuid import UUID


class WorkingMemory:
    def __init__(self) -> None:
        self._data: dict[UUID, dict[str, str]] = {}

    async def put(self, run_id: UUID, key: str, value: str) -> None:
        self._data.setdefault(run_id, {})[key] = value

    async def get(self, run_id: UUID, key: str) -> str | None:
        return self._data.get(run_id, {}).get(key)

    async def clear(self, run_id: UUID) -> None:
        self._data.pop(run_id, None)

    async def all(self, run_id: UUID) -> dict[str, str]:
        return dict(self._data.get(run_id, {}))
