from typing import List

from pydantic import BaseModel, Field


class ReviewerEngineConfig(BaseModel):
    enabled: bool = Field(default=True)
    top_n: int = Field(default=3, ge=1, le=10)
    minimum_recommendation_score: float = Field(default=20.0, ge=0.0, le=100.0)
    
    history_days: int = Field(default=365, ge=30, le=3650)
    max_history_commits: int = Field(default=2000, ge=100, le=10000)
    
    allow_external_codeowners: bool = Field(default=False)
    
    eligible_roles: List[str] = Field(default_factory=lambda: ["ADMIN", "MAINTAINER", "REVIEWER"])
