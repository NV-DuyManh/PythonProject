from typing import List, Optional

from pydantic import BaseModel


class Reason(BaseModel):
    finding_id: Optional[int]
    severity: Optional[str]
    penalty: float
    reason: str

class ComponentResult(BaseModel):
    name: str
    score: Optional[float]
    canonical_weight: float
    included: bool
    finding_count: int
    penalty_total: float
    reasons: List[Reason]

class QualityScoreResult(BaseModel):
    overall_score: float
    grade: str
    is_complete: bool
    available_weight: float
    missing_dimensions: List[str]
    components: List[ComponentResult]
    calculation_version: str
