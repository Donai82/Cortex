from uuid import UUID, uuid4

GoalId = UUID
RunId = UUID
PlanId = UUID
EventId = UUID


def new_id() -> UUID:
    return uuid4()
