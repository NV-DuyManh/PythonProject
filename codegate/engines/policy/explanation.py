from typing import Any, Dict, List

from codegate.engines.policy.schemas import PolicyEvaluationResult


def build_evaluation_breakdown(result: PolicyEvaluationResult) -> Dict[str, Any]:
    return {
        "decision": result.decision.value,
        "rules": [
            {
                "rule_id": r.rule_id,
                "rule_name": r.rule_name,
                "status": r.status.value,
                "actual_value": r.actual_value,
                "expected_value": r.expected_value,
                "reason": r.reason
            }
            for r in result.rules
        ],
        "flags": result.flags
    }
