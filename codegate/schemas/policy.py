from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from codegate.engines.policy.schemas import PolicyConfig

class QualityPolicyResponse(BaseModel):
    id: int
    repository_id: int
    name: str
    policy_engine_version: str
    revision: int
    
    quality_pass_threshold: float
    quality_block_threshold: float
    
    risk_warning_threshold: float
    risk_block_threshold: float
    
    max_critical_findings: int
    max_high_security_findings: int
    
    require_quality_score: bool
    require_risk_score: bool
    
    require_complete_quality: bool
    require_complete_risk: bool
    
    active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class ConfigDict:
        from_attributes = True

class QualityPolicyUpdate(BaseModel):
    quality_pass_threshold: Optional[float] = Field(None, ge=0, le=100)
    quality_block_threshold: Optional[float] = Field(None, ge=0, le=100)
    
    risk_warning_threshold: Optional[float] = Field(None, ge=0, le=100)
    risk_block_threshold: Optional[float] = Field(None, ge=0, le=100)
    
    max_critical_findings: Optional[int] = Field(None, ge=0)
    max_high_security_findings: Optional[int] = Field(None, ge=0)
    
    require_quality_score: Optional[bool] = None
    require_risk_score: Optional[bool] = None
    
    require_complete_quality: Optional[bool] = None
    require_complete_risk: Optional[bool] = None

class PolicyEvaluationResponse(BaseModel):
    id: int
    analysis_run_id: int
    policy_id: int
    policy_engine_version: str
    policy_revision: int
    
    decision: Optional[str]
    
    passed_rules_count: Optional[int]
    warning_rules_count: Optional[int]
    blocked_rules_count: Optional[int]
    
    breakdown_json: Optional[Any]
    flags_json: Optional[Any]
    config_snapshot_json: Optional[Any]
    
    evaluation_status: str
    error_message: Optional[str]
    
    github_check_run_id: Optional[int]
    github_publish_status: Optional[str]
    github_publish_error: Optional[str]
    published_at: Optional[datetime]
    
    created_at: datetime
    updated_at: Optional[datetime]

    class ConfigDict:
        from_attributes = True
