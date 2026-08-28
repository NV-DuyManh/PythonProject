from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class ReasonResponse(BaseModel):
    finding_id: Optional[int]
    severity: Optional[str]
    penalty: float
    reason: str

class ComponentResultResponse(BaseModel):
    name: str
    score: Optional[float]
    canonical_weight: float
    included: bool
    finding_count: int
    penalty_total: float
    reasons: List[ReasonResponse]

class QualityScoreResponse(BaseModel):
    id: int
    analysis_run_id: int
    overall_score: float
    grade: str
    is_complete: bool
    available_weight: float
    missing_dimensions: List[str]
    components: List[ComponentResultResponse]
    calculation_version: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PullRequestQualitySummary(BaseModel):
    latest_quality_score: Optional[float]
    latest_quality_grade: Optional[str]
    quality_complete: Optional[bool]
