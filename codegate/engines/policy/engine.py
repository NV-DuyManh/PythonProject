from typing import Any, List, Optional

from codegate.database.models.analysis import Finding, QualityScore, RiskScore
from codegate.engines.policy.rules import (
    evaluate_max_critical_findings,
    evaluate_max_high_security_findings,
    evaluate_max_risk_score,
    evaluate_min_quality_score,
    evaluate_quality_availability,
    evaluate_quality_completeness,
    evaluate_risk_availability,
    evaluate_risk_completeness,
)
from codegate.engines.policy.schemas import PolicyConfig, PolicyDecision, PolicyEvaluationResult


class QualityPolicyEngine:
    @staticmethod
    def evaluate(
        config: PolicyConfig,
        quality_score: Optional[QualityScore],
        risk_score: Optional[RiskScore],
        findings: List[Finding],
        test_run: Optional[Any] = None,
        coverage_report: Optional[Any] = None
    ) -> PolicyEvaluationResult:
        rules_results = []
        
        # 1. Quality
        rules_results.append(evaluate_quality_availability(config, quality_score))
        res = evaluate_quality_completeness(config, quality_score)
        if res: rules_results.append(res)
        res = evaluate_min_quality_score(config, quality_score)
        if res: rules_results.append(res)
        
        # 2. Risk
        rules_results.append(evaluate_risk_availability(config, risk_score))
        res = evaluate_risk_completeness(config, risk_score)
        if res: rules_results.append(res)
        res = evaluate_max_risk_score(config, risk_score)
        if res: rules_results.append(res)
        
        # 3. Findings
        rules_results.append(evaluate_max_critical_findings(config, findings))
        rules_results.append(evaluate_max_high_security_findings(config, findings))
        
        # 4. Testing
        from codegate.engines.policy.rules import evaluate_changed_code_coverage, evaluate_test_result
        res = evaluate_test_result(config, test_run)
        if res: rules_results.append(res)
        res = evaluate_changed_code_coverage(config, coverage_report)
        if res: rules_results.append(res)
        
        # Aggregate decision (BLOCK > WARNING > PASS)
        overall_decision = PolicyDecision.PASS
        flags = []
        for r in rules_results:
            if r.status == PolicyDecision.BLOCK:
                overall_decision = PolicyDecision.BLOCK
            elif r.status == PolicyDecision.WARNING and overall_decision != PolicyDecision.BLOCK:
                overall_decision = PolicyDecision.WARNING
                
            flags.extend(r.flags)
            
        # Deduplicate flags
        flags = list(set(flags))
        
        return PolicyEvaluationResult(
            decision=overall_decision,
            rules=rules_results,
            flags=flags
        )
