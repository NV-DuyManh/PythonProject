from typing import List, Optional, Any, Dict
from pydantic import BaseModel

class RiskReason(BaseModel):
    finding_id: Optional[int]
    rule_id: Optional[str]
    file_path: Optional[str]
    risk_contribution: float
    description: str

class RiskComponentResult(BaseModel):
    name: str
    risk: Optional[float]
    canonical_weight: float
    effective_weight: float
    included: bool
    input_facts: Dict[str, Any]
    counted_findings: int
    ignored_findings: int
    reasons: List[RiskReason]
    flags: List[str]

class RiskScoreResult(BaseModel):
    overall_risk: float
    risk_level: str
    is_complete: bool
    available_weight: float
    missing_dimensions: List[str]
    components: List[RiskComponentResult]
    flags: List[str]
    calculation_version: str
