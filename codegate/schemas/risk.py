from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class RiskReasonResponse(BaseModel):
    finding_id: Optional[int]
    rule_id: Optional[str]
    file_path: Optional[str]
    risk_contribution: float
    description: str

class RiskComponentResultResponse(BaseModel):
    name: str
    risk: Optional[float]
    canonical_weight: float
    effective_weight: float
    included: bool
    input_facts: Dict[str, Any]
    counted_findings: int
    ignored_findings: int
    reasons: List[RiskReasonResponse]
    flags: List[str]

class RiskScoreResponse(BaseModel):
    id: int
    analysis_run_id: int
    overall_risk: float
    risk_level: str
    
    change_surface_risk: Optional[float]
    sensitive_path_risk: Optional[float]
    security_risk: Optional[float]
    complexity_risk: Optional[float]
    
    is_complete: bool
    available_weight: float
    missing_dimensions: List[str]
    
    components: List[RiskComponentResultResponse]
    flags: List[str]
    
    calculation_version: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
