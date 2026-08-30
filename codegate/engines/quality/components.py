from typing import List, Dict, Any, Optional
from codegate.database.models.analysis import Finding, CodeMetric
from codegate.engines.quality.schemas import ComponentResult, Reason
from codegate.engines.quality.config import CANONICAL_WEIGHTS, SEVERITY_PENALTIES, COMPLEXITY_GRADE_PENALTIES

def clamp(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    return max(min_val, min(value, max_val))

def _calculate_findings_component(
    name: str,
    weight: float,
    findings: List[Finding],
    included: bool = True
) -> ComponentResult:
    if not included:
        return ComponentResult(
            name=name,
            score=None,
            canonical_weight=weight,
            included=False,
            finding_count=0,
            penalty_total=0.0,
            reasons=[Reason(finding_id=None, severity=None, penalty=0.0, reason=f"{name.capitalize()} is missing or not applicable.")]
        )

    penalty_total = 0.0
    reasons = []

    for f in findings:
        severity_str = f.severity.value if hasattr(f.severity, "value") else str(f.severity)
        penalty = float(SEVERITY_PENALTIES.get(severity_str, 0))
        penalty_total += penalty
        reasons.append(Reason(
            finding_id=f.id,
            severity=severity_str,
            penalty=penalty,
            reason=f"{f.source}: {f.rule_id or f.title}"
        ))

    score = clamp(100.0 - penalty_total)
    
    return ComponentResult(
        name=name,
        score=score,
        canonical_weight=weight,
        included=True,
        finding_count=len(findings),
        penalty_total=penalty_total,
        reasons=reasons
    )

def calculate_code_quality(findings: List[Finding]) -> ComponentResult:
    # Code Quality uses RUFF on changed code
    eligible = [f for f in findings if f.source == "RUFF" and (f.is_new_code or f.is_changed_file)]
    return _calculate_findings_component(
        "code_quality",
        CANONICAL_WEIGHTS["code_quality"],
        eligible
    )

def calculate_security(findings: List[Finding]) -> ComponentResult:
    # Security uses BANDIT and AI (if categorized as security, though AI doesn't have categories right now, we assume BANDIT)
    eligible = [f for f in findings if f.source == "BANDIT" and (f.is_new_code or f.is_changed_file)]
    
    # Deduplicate based on rule_id, file, line
    fingerprints = set()
    deduped = []
    for f in eligible:
        fp = (f.source, f.rule_id, f.file_path, f.start_line)
        if fp not in fingerprints:
            fingerprints.add(fp)
            deduped.append(f)
            
    return _calculate_findings_component(
        "security",
        CANONICAL_WEIGHTS["security"],
        deduped
    )

def calculate_ai_review(findings: List[Finding]) -> ComponentResult:
    # AI Review is for AI findings. We don't strictly require is_changed_file=True for AI findings
    # if it's a PR level comment. But if it has is_changed_file=False explicitly, we skip.
    eligible = [f for f in findings if f.source == "AI" and f.is_changed_file is not False]
    return _calculate_findings_component(
        "ai_review",
        CANONICAL_WEIGHTS["ai_review"],
        eligible
    )

def calculate_complexity(metrics: List[CodeMetric], findings: List[Finding]) -> ComponentResult:
    # Complexity uses Radon
    # We should only consider metrics on changed files. 
    # But for Radon metrics, is_changed_file isn't on the metric. 
    # We will assume all metrics calculated are for changed files (RadonAnalyzer already filters in the runner).
    
    eligible = [m for m in metrics if m.analyzer == "RADON" and m.metric_name == "cyclomatic_complexity"]
    
    penalty_total = 0.0
    reasons = []

    for m in eligible:
        grade = m.grade or "A"
        penalty = float(COMPLEXITY_GRADE_PENALTIES.get(grade, 0))
        if penalty > 0:
            penalty_total += penalty
            reasons.append(Reason(
                finding_id=m.id, # id from metric
                severity=grade,
                penalty=penalty,
                reason=f"Radon Complexity: {m.symbol} is grade {grade}"
            ))

    score = clamp(100.0 - penalty_total)
    
    return ComponentResult(
        name="complexity",
        score=score,
        canonical_weight=CANONICAL_WEIGHTS["complexity"],
        included=True,
        finding_count=len(eligible),
        penalty_total=penalty_total,
        reasons=reasons
    )

def calculate_maintainability() -> ComponentResult:
    return _calculate_findings_component(
        "maintainability",
        CANONICAL_WEIGHTS["maintainability"],
        [],
        included=False
    )

def calculate_testing(testing_score: Optional[float] = None) -> ComponentResult:
    if testing_score is not None:
        return ComponentResult(
            name="testing",
            score=testing_score,
            canonical_weight=CANONICAL_WEIGHTS["testing"],
            included=True,
            finding_count=0,
            penalty_total=0.0,
            reasons=[Reason(finding_id=None, severity=None, reason=f"Score derived from test execution", penalty=0.0)]
        )
        
    return _calculate_findings_component(
        "testing",
        CANONICAL_WEIGHTS["testing"],
        [],
        included=False
    )
