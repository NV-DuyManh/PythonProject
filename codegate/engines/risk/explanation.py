from typing import Dict, Any
from codegate.engines.risk.schemas import RiskScoreResult

def build_risk_breakdown(result: RiskScoreResult) -> Dict[str, Any]:
    return result.model_dump()
