from .models import SemanticFact


class SemanticMemory:
    def __init__(self) -> None:
        self._facts: list[SemanticFact] = []

    async def add(self, fact: SemanticFact) -> None:
        self._facts.append(fact)

    async def list(self) -> list[SemanticFact]:
        return list(self._facts)
