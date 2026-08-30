from typing import Optional, List
from codegate.database.models.analysis import QualityScore, RiskScore, Finding, Severity, Source
from codegate.engines.policy.schemas import PolicyConfig, RuleResult, PolicyDecision
from codegate.engines.policy.config import *

def evaluate_quality_availability(config: PolicyConfig, score: Optional[QualityScore]) -> RuleResult:
    if score is not None:
        return RuleResult(
            rule_id=RULE_ID_QUALITY_AVAILABILITY,
            rule_name="Quality Score Availability",
            status=PolicyDecision.PASS,
            actual_value="Available",
            expected_value="Available",
            reason="Quality score is present."
        )
    
    if config.require_quality_score:
        return RuleResult(
            rule_id=RULE_ID_QUALITY_AVAILABILITY,
            rule_name="Quality Score Availability",
            status=PolicyDecision.BLOCK,
            actual_value="Missing",
            expected_value="Available",
            reason="Quality score is required by policy but is missing.",
            flags=["MISSING_QUALITY"]
        )
    else:
        return RuleResult(
            rule_id=RULE_ID_QUALITY_AVAILABILITY,
            rule_name="Quality Score Availability",
            status=PolicyDecision.WARNING,
            actual_value="Missing",
            expected_value="Available",
            reason="Quality score is missing (not required to block).",
            flags=["MISSING_QUALITY"]
        )


def evaluate_quality_completeness(config: PolicyConfig, score: Optional[QualityScore]) -> Optional[RuleResult]:
    if score is None:
        return None
        
    if score.is_complete:
        return RuleResult(
            rule_id=RULE_ID_QUALITY_COMPLETENESS,
            rule_name="Quality Score Completeness",
            status=PolicyDecision.PASS,
            actual_value="Complete",
            expected_value="Complete",
            reason="Quality analysis is complete."
        )

    if config.require_complete_quality:
        return RuleResult(
            rule_id=RULE_ID_QUALITY_COMPLETENESS,
            rule_name="Quality Score Completeness",
            status=PolicyDecision.BLOCK,
            actual_value="Partial",
            expected_value="Complete",
            reason="Complete quality analysis is required but is partial.",
            flags=["PARTIAL_QUALITY"]
        )
    else:
        return RuleResult(
            rule_id=RULE_ID_QUALITY_COMPLETENESS,
            rule_name="Quality Score Completeness",
            status=PolicyDecision.WARNING,
            actual_value="Partial",
            expected_value="Complete",
            reason="Quality analysis is partial (not required to block).",
            flags=["PARTIAL_QUALITY"]
        )


def evaluate_min_quality_score(config: PolicyConfig, score: Optional[QualityScore]) -> Optional[RuleResult]:
    if score is None:
        return None
        
    val = score.overall_score
    if val >= config.quality_pass_threshold:
        return RuleResult(
            rule_id=RULE_ID_MIN_QUALITY_SCORE,
            rule_name="Minimum Quality Score",
            status=PolicyDecision.PASS,
            actual_value=val,
            expected_value=f">= {config.quality_pass_threshold}",
            reason=f"Quality score {val} meets the pass threshold."
        )
    elif val >= config.quality_block_threshold:
        return RuleResult(
            rule_id=RULE_ID_MIN_QUALITY_SCORE,
            rule_name="Minimum Quality Score",
            status=PolicyDecision.WARNING,
            actual_value=val,
            expected_value=f">= {config.quality_pass_threshold}",
            reason=f"Quality score {val} is below pass threshold but above block threshold.",
            flags=["LOW_QUALITY"]
        )
    else:
        return RuleResult(
            rule_id=RULE_ID_MIN_QUALITY_SCORE,
            rule_name="Minimum Quality Score",
            status=PolicyDecision.BLOCK,
            actual_value=val,
            expected_value=f">= {config.quality_block_threshold}",
            reason=f"Quality score {val} is below the block threshold {config.quality_block_threshold}.",
            flags=["LOW_QUALITY"]
        )


def evaluate_risk_availability(config: PolicyConfig, score: Optional[RiskScore]) -> RuleResult:
    if score is not None:
        return RuleResult(
            rule_id=RULE_ID_RISK_AVAILABILITY,
            rule_name="Risk Score Availability",
            status=PolicyDecision.PASS,
            actual_value="Available",
            expected_value="Available",
            reason="Risk score is present."
        )
    
    if config.require_risk_score:
        return RuleResult(
            rule_id=RULE_ID_RISK_AVAILABILITY,
            rule_name="Risk Score Availability",
            status=PolicyDecision.BLOCK,
            actual_value="Missing",
            expected_value="Available",
            reason="Risk score is required by policy but is missing.",
            flags=["MISSING_RISK"]
        )
    else:
        return RuleResult(
            rule_id=RULE_ID_RISK_AVAILABILITY,
            rule_name="Risk Score Availability",
            status=PolicyDecision.WARNING,
            actual_value="Missing",
            expected_value="Available",
            reason="Risk score is missing (not required to block).",
            flags=["MISSING_RISK"]
        )


def evaluate_risk_completeness(config: PolicyConfig, score: Optional[RiskScore]) -> Optional[RuleResult]:
    if score is None:
        return None
        
    if score.is_complete:
        return RuleResult(
            rule_id=RULE_ID_RISK_COMPLETENESS,
            rule_name="Risk Score Completeness",
            status=PolicyDecision.PASS,
            actual_value="Complete",
            expected_value="Complete",
            reason="Risk analysis is complete."
        )

    if config.require_complete_risk:
        return RuleResult(
            rule_id=RULE_ID_RISK_COMPLETENESS,
            rule_name="Risk Score Completeness",
            status=PolicyDecision.BLOCK,
            actual_value="Partial",
            expected_value="Complete",
            reason="Complete risk analysis is required but is partial.",
            flags=["PARTIAL_RISK"]
        )
    else:
        return RuleResult(
            rule_id=RULE_ID_RISK_COMPLETENESS,
            rule_name="Risk Score Completeness",
            status=PolicyDecision.WARNING,
            actual_value="Partial",
            expected_value="Complete",
            reason="Risk analysis is partial (not required to block).",
            flags=["PARTIAL_RISK"]
        )


def evaluate_max_risk_score(config: PolicyConfig, score: Optional[RiskScore]) -> Optional[RuleResult]:
    if score is None:
        return None
        
    val = score.overall_risk
    if val < config.risk_warning_threshold:
        return RuleResult(
            rule_id=RULE_ID_MAX_RISK_SCORE,
            rule_name="Maximum Risk Score",
            status=PolicyDecision.PASS,
            actual_value=val,
            expected_value=f"< {config.risk_warning_threshold}",
            reason=f"Risk score {val} is below the warning threshold."
        )
    elif val < config.risk_block_threshold:
        return RuleResult(
            rule_id=RULE_ID_MAX_RISK_SCORE,
            rule_name="Maximum Risk Score",
            status=PolicyDecision.WARNING,
            actual_value=val,
            expected_value=f"< {config.risk_warning_threshold}",
            reason=f"Risk score {val} is at or above warning threshold but below block threshold.",
            flags=["HIGH_RISK"]
        )
    else:
        return RuleResult(
            rule_id=RULE_ID_MAX_RISK_SCORE,
            rule_name="Maximum Risk Score",
            status=PolicyDecision.BLOCK,
            actual_value=val,
            expected_value=f"< {config.risk_block_threshold}",
            reason=f"Risk score {val} meets or exceeds the block threshold {config.risk_block_threshold}.",
            flags=["HIGH_RISK"]
        )


def _is_new_or_changed(finding: Finding) -> bool:
    return bool(finding.is_new_code) or bool(finding.is_changed_file)


def evaluate_max_critical_findings(config: PolicyConfig, findings: List[Finding]) -> RuleResult:
    # Only count critical findings that are on changed or new code
    critical_count = sum(
        1 for f in findings 
        if f.severity == Severity.CRITICAL and _is_new_or_changed(f)
    )
    
    if critical_count <= config.max_critical_findings:
        return RuleResult(
            rule_id=RULE_ID_MAX_CRITICAL_FINDINGS,
            rule_name="Max Critical Findings",
            status=PolicyDecision.PASS,
            actual_value=critical_count,
            expected_value=f"<= {config.max_critical_findings}",
            reason=f"Found {critical_count} critical findings."
        )
    else:
        return RuleResult(
            rule_id=RULE_ID_MAX_CRITICAL_FINDINGS,
            rule_name="Max Critical Findings",
            status=PolicyDecision.BLOCK,
            actual_value=critical_count,
            expected_value=f"<= {config.max_critical_findings}",
            reason=f"Found {critical_count} critical findings on changed code, exceeding limit of {config.max_critical_findings}.",
            flags=["CRITICAL_FINDING"]
        )


def evaluate_max_high_security_findings(config: PolicyConfig, findings: List[Finding]) -> RuleResult:
    # Source is BANDIT or (Source is AI and category == SECURITY)
    # Severity is HIGH or CRITICAL
    # is_new_or_changed is True
    security_count = 0
    for f in findings:
        if _is_new_or_changed(f):
            if f.severity in (Severity.HIGH, Severity.CRITICAL):
                if f.source == Source.BANDIT:
                    security_count += 1
                elif f.source == Source.AI and (f.category or "").upper() == "SECURITY":
                    security_count += 1
                    
    if security_count <= config.max_high_security_findings:
        return RuleResult(
            rule_id=RULE_ID_MAX_HIGH_SECURITY_FINDINGS,
            rule_name="Max High/Critical Security Findings",
            status=PolicyDecision.PASS,
            actual_value=security_count,
            expected_value=f"<= {config.max_high_security_findings}",
            reason=f"Found {security_count} high/critical security findings."
        )
    else:
        return RuleResult(
            rule_id=RULE_ID_MAX_HIGH_SECURITY_FINDINGS,
            rule_name="Max High/Critical Security Findings",
            status=PolicyDecision.BLOCK,
            actual_value=security_count,
            expected_value=f"<= {config.max_high_security_findings}",
            reason=f"Found {security_count} high/critical security findings on changed code, exceeding limit of {config.max_high_security_findings}.",
            flags=["HIGH_SECURITY_FINDING"]
        )
