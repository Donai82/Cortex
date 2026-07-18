from collections import defaultdict

import structlog

from cortex.core.events import Event

from .interface import EventBus, Handler


class InMemoryEventBus(EventBus):
    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)
        self._log = structlog.get_logger(__name__)

    async def subscribe(self, event_type: str, handler: Handler) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: Event) -> None:
        self._log.info("event_published", event_type=event.event_type, event_id=str(event.event_id))
        for handler in self._handlers.get(event.event_type, []):
            try:
                await handler(event)
            except Exception as exc:  # handlers are isolated by design
                self._log.error("event_handler_failed", error_type=type(exc).__name__)
