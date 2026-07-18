from typing import Protocol

from .models import Evaluation


class Evaluator(Protocol):
    async def evaluate(
        self,
        completed: bool,
        limits_respected: bool,
        tasks_finished: bool,
        policies_obeyed: bool,
        errors_handled: bool,
    ) -> Evaluation: ...
