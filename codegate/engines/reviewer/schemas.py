from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ReviewerIdentityInfo(BaseModel):
    user_id: int
    provider_username: str
    email: Optional[str] = None
    is_author: bool = False

class CodeownersMatch(BaseModel):
    pattern: str
    owner: str

class RecommendationCandidate(BaseModel):
    user_id: int
    provider_username: str
    
    overall_score: float = 0.0
    
    codeowners_score: Optional[float] = None
    exact_file_score: Optional[float] = None
    directory_score: Optional[float] = None
    recency_score: Optional[float] = None
    
    exact_file_commits: int = 0
    directory_commits: int = 0
    
    file_coverage_percent: Optional[float] = None
    
    matched_files: List[str] = Field(default_factory=list)
    reasons: List[str] = Field(default_factory=list)
    
    # Internal usage
    evidence: Dict[str, Any] = Field(default_factory=dict)
    
    def to_db_dict(self, rank: int) -> dict:
        import json
        return {
            "user_id": self.user_id,
            "provider_username": self.provider_username,
            "rank": rank,
            "overall_score": self.overall_score,
            "codeowners_score": self.codeowners_score,
            "exact_file_score": self.exact_file_score,
            "directory_score": self.directory_score,
            "recency_score": self.recency_score,
            "exact_file_commits": self.exact_file_commits,
            "directory_commits": self.directory_commits,
            "file_coverage_percent": self.file_coverage_percent,
            "matched_files_json": json.dumps(self.matched_files),
            "reasons_json": json.dumps(self.reasons),
            "evidence_json": json.dumps(self.evidence)
        }

class ReviewerRecommendationResult(BaseModel):
    status: str
    engine_version: str
    
    recommendations: List[RecommendationCandidate] = Field(default_factory=list)
    
    eligible_candidate_count: int = 0
    recommended_candidate_count: int = 0
    
    is_complete: bool = True
    available_weight: float = 100.0
    
    missing_sources: List[str] = Field(default_factory=list)
    unresolved_codeowners: List[str] = Field(default_factory=list)
    
    error_message: Optional[str] = None
