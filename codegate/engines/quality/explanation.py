from typing import Any, Dict

from codegate.engines.quality.schemas import QualityScoreResult


def build_breakdown_json(result: QualityScoreResult) -> Dict[str, Any]:
    return result.model_dump()
