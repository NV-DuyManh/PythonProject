from enum import Enum
from typing import List, Optional, Any
from pydantic import BaseModel, Field

class PolicyDecision(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    BLOCK = "BLOCK"

class PolicyConfig(BaseModel):
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


class RuleResult(BaseModel):
    rule_id: str
    rule_name: str
    status: PolicyDecision
    actual_value: Any
    expected_value: str
    reason: str
    flags: List[str] = Field(default_factory=list)


class PolicyEvaluationResult(BaseModel):
    decision: PolicyDecision
    rules: List[RuleResult] = Field(default_factory=list)
    flags: List[str] = Field(default_factory=list)
    
    @property
    def passed_rules_count(self) -> int:
        return sum(1 for r in self.rules if r.status == PolicyDecision.PASS)

    @property
    def warning_rules_count(self) -> int:
        return sum(1 for r in self.rules if r.status == PolicyDecision.WARNING)

    @property
    def blocked_rules_count(self) -> int:
        return sum(1 for r in self.rules if r.status == PolicyDecision.BLOCK)
