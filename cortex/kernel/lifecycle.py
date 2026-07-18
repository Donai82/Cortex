from cortex.core.exceptions import InvalidTransitionError

from .state import RunStatus

TRANSITIONS = {
    RunStatus.CREATED: RunStatus.PLANNING,
    RunStatus.PLANNING: RunStatus.RETRIEVING_MEMORY,
    RunStatus.RETRIEVING_MEMORY: RunStatus.DECIDING,
    RunStatus.DECIDING: RunStatus.EXECUTING,
    RunStatus.EXECUTING: RunStatus.REFLECTING,
    RunStatus.REFLECTING: RunStatus.EVALUATING,
    RunStatus.EVALUATING: RunStatus.COMPLETED,
}


def next_status(status: RunStatus) -> RunStatus:
    if status not in TRANSITIONS:
        raise InvalidTransitionError(f"No transition from {status}")
    return TRANSITIONS[status]
