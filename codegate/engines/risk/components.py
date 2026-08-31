import fnmatch
from typing import Any, Dict, List, Tuple

from codegate.database.models.analysis import AnalyzerRun, CodeMetric, Finding, Status
from codegate.database.models.pull_request import PullRequest, PullRequestFile
from codegate.engines.risk.config import (
    CANONICAL_WEIGHTS,
    COMPLEXITY_MAPPING,
    FILES_RISK_MAPPING,
    LINES_RISK_MAPPING,
    SECURITY_POINTS,
    SENSITIVE_PATHS_TIERS,
)
from codegate.engines.risk.schemas import RiskComponentResult, RiskReason


def _clamp(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    return max(min_val, min(value, max_val))

def calculate_security_risk(findings: List[Finding], analyzer_runs: List[AnalyzerRun]) -> RiskComponentResult:
    weight = CANONICAL_WEIGHTS["security"]
    
    # Check Bandit status
    bandit_runs = [r for r in analyzer_runs if r.analyzer == "BANDIT"]
    if bandit_runs:
        last_bandit = sorted(bandit_runs, key=lambda x: x.created_at, reverse=True)[0]
        if last_bandit.status in (Status.FAILED, Status.TIMEOUT):
            return RiskComponentResult(
                name="security", risk=None, canonical_weight=weight, effective_weight=0.0,
                included=False, input_facts={"bandit_status": last_bandit.status.value},
                counted_findings=0, ignored_findings=0, reasons=[], flags=["PARTIAL_ANALYSIS"]
            )
            
    # Filter findings
    relevant_findings = [f for f in findings if (f.source == "BANDIT" or (f.source == "AI" and f.category == "SECURITY"))]
    
    counted = []
    ignored_count = 0
    fingerprints = set()
    
    for f in relevant_findings:
        if not (f.is_new_code or f.is_changed_file):
            ignored_count += 1
            continue
            
        fp = (f.source, f.rule_id or f.category, f.file_path, f.start_line, f.title)
        if fp not in fingerprints:
            fingerprints.add(fp)
            counted.append(f)
            
    risk_sum = 0.0
    reasons = []
    has_high_security = False
    
    for f in counted:
        sev_str = f.severity.value if hasattr(f.severity, "value") else str(f.severity)
        pts = float(SECURITY_POINTS.get(sev_str, 0))
        risk_sum += pts
        if pts >= SECURITY_POINTS["HIGH"]:
            has_high_security = True
            
        reasons.append(RiskReason(
            finding_id=f.id,
            rule_id=f.rule_id,
            file_path=f.file_path,
            risk_contribution=pts,
            description=f"{f.source} - {f.title} ({sev_str})"
        ))
        
    final_risk = _clamp(risk_sum)
    flags = ["HIGH_SECURITY_FINDING"] if has_high_security else []
    
    return RiskComponentResult(
        name="security", risk=final_risk, canonical_weight=weight, effective_weight=0.0,
        included=True, input_facts={"total_points": risk_sum},
        counted_findings=len(counted), ignored_findings=ignored_count,
        reasons=reasons, flags=flags
    )

def _get_mapped_value(val: int, mapping: List[Tuple[int, float, float]]) -> float:
    for min_v, max_v, risk_v in mapping:
        if min_v <= val <= max_v:
            return risk_v
    return 0.0

def calculate_change_surface_risk(pr: PullRequest) -> RiskComponentResult:
    weight = CANONICAL_WEIGHTS["change_surface"]
    
    additions = pr.additions or 0
    deletions = pr.deletions or 0
    changed_lines = additions + deletions
    changed_files = pr.changed_files or 0
    
    lines_risk = _get_mapped_value(changed_lines, LINES_RISK_MAPPING)
    files_risk = _get_mapped_value(changed_files, FILES_RISK_MAPPING)
    
    risk = _clamp(lines_risk * 0.70 + files_risk * 0.30)
    
    flags = ["LARGE_CHANGE"] if risk >= 70 else []
    
    reasons = [
        RiskReason(finding_id=None, rule_id=None, file_path=None, risk_contribution=lines_risk * 0.70, description=f"Lines risk: {lines_risk} (changed_lines={changed_lines})"),
        RiskReason(finding_id=None, rule_id=None, file_path=None, risk_contribution=files_risk * 0.30, description=f"Files risk: {files_risk} (changed_files={changed_files})")
    ]
    
    return RiskComponentResult(
        name="change_surface", risk=risk, canonical_weight=weight, effective_weight=0.0,
        included=True, input_facts={"additions": additions, "deletions": deletions, "changed_files": changed_files},
        counted_findings=0, ignored_findings=0, reasons=reasons, flags=flags
    )

def calculate_sensitive_path_risk(pr_files: List[PullRequestFile]) -> RiskComponentResult:
    weight = CANONICAL_WEIGHTS["sensitive_path"]
    
    max_risk = 0.0
    reasons = []
    
    # We must not trigger on README according to prompt? Actually it just says: "README không được trigger." - which means it won't match any patterns, or we explicitly ignore it.
    # The glob patterns don't match README.md anyway.
    
    for f in pr_files:
        if not f.filename:
            continue
            
        norm_path = f.filename.replace("\\", "/")
        
        file_max = 0.0
        best_tier = None
        best_pattern = None
        
        for tier, data in SENSITIVE_PATHS_TIERS.items():
            r = float(data["risk"])
            for pat in data["patterns"]:
                if fnmatch.fnmatch(norm_path, pat) or fnmatch.fnmatch(norm_path, f"*/{pat}") or fnmatch.fnmatch(norm_path, f"*{pat}*"):
                    # Use standard glob matching
                    # The prompt says "**" which in fnmatch needs to be handled properly, 
                    # Python's fnmatch handles * to match everything including /.
                    pass
                if fnmatch.fnmatch(norm_path, pat):
                    if r > file_max:
                        file_max = r
                        best_tier = tier
                        best_pattern = pat
                        
        if file_max > 0:
            if file_max > max_risk:
                max_risk = file_max
            reasons.append(RiskReason(
                finding_id=None, rule_id=best_tier, file_path=norm_path, risk_contribution=file_max,
                description=f"Matched {best_pattern}"
            ))
            
    flags = ["SENSITIVE_AUTH_CHANGE"] if max_risk == 100 else []
    
    return RiskComponentResult(
        name="sensitive_path", risk=max_risk, canonical_weight=weight, effective_weight=0.0,
        included=True, input_facts={"files_checked": len(pr_files)},
        counted_findings=len(reasons), ignored_findings=0, reasons=reasons, flags=flags
    )

def calculate_complexity_risk(metrics: List[CodeMetric], analyzer_runs: List[AnalyzerRun]) -> RiskComponentResult:
    weight = CANONICAL_WEIGHTS["complexity"]
    
    # Check Radon status
    radon_runs = [r for r in analyzer_runs if r.analyzer == "RADON"]
    if radon_runs:
        last_radon = sorted(radon_runs, key=lambda x: x.created_at, reverse=True)[0]
        if last_radon.status in (Status.FAILED, Status.TIMEOUT):
            return RiskComponentResult(
                name="complexity", risk=None, canonical_weight=weight, effective_weight=0.0,
                included=False, input_facts={"radon_status": last_radon.status.value},
                counted_findings=0, ignored_findings=0, reasons=[], flags=["PARTIAL_ANALYSIS"]
            )
            
    # Radon FAILED/TIMEOUT handled. Missing is handled as success + no finding if radon_runs is empty? Wait, if radon_runs is empty, is it missing? 
    # The prompt says "Nếu Radon FAILED/TIMEOUT: complexity_risk = null". And "Nếu Radon SUCCESS và không có applicable complex symbol: complexity_risk = 0".
    # What if there are NO radon_runs at all? Then we treat it as missing.
    if not radon_runs:
        return RiskComponentResult(
            name="complexity", risk=None, canonical_weight=weight, effective_weight=0.0,
            included=False, input_facts={"radon_status": "MISSING"},
            counted_findings=0, ignored_findings=0, reasons=[], flags=["PARTIAL_ANALYSIS"]
        )
        
    relevant = [m for m in metrics if m.analyzer == "RADON" and m.metric_name == "cyclomatic_complexity"]
    
    max_risk = 0.0
    reasons = []
    has_high = False
    
    for m in relevant:
        grade = m.grade or "A"
        r = float(COMPLEXITY_MAPPING.get(grade, 0))
        if r > max_risk:
            max_risk = r
        if r >= 75:
            has_high = True
            
        reasons.append(RiskReason(
            finding_id=m.id, rule_id=grade, file_path=m.file_path, risk_contribution=r,
            description=f"{m.symbol} complexity is {grade}"
        ))
        
    flags = ["HIGH_COMPLEXITY_SYMBOL"] if has_high else []
    
    return RiskComponentResult(
        name="complexity", risk=max_risk, canonical_weight=weight, effective_weight=0.0,
        included=True, input_facts={"metrics_count": len(relevant)},
        counted_findings=len(relevant), ignored_findings=0, reasons=reasons, flags=flags
    )
