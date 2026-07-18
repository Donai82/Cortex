from .models import Evaluation


class RuleBasedEvaluator:
    async def evaluate(
        self,
        completed: bool,
        limits_respected: bool,
        tasks_finished: bool,
        policies_obeyed: bool,
        errors_handled: bool,
    ) -> Evaluation:
        checks = [completed, limits_respected, tasks_finished, policies_obeyed, errors_handled]
        score = sum(checks) / len(checks)
        return Evaluation(
            score=score,
            passed=score == 1,
            reasons=["all checks passed"] if score == 1 else ["one or more checks failed"],
            metrics={"checks": float(sum(checks))},
        )
