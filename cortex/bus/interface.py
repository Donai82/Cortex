from collections.abc import Awaitable, Callable
from typing import Protocol

from cortex.core.events import Event

Handler = Callable[[Event], Awaitable[None]]


class EventBus(Protocol):
    async def subscribe(self, event_type: str, handler: Handler) -> None: ...
    async def publish(self, event: Event) -> None: ...
