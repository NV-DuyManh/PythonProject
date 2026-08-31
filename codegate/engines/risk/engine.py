from typing import List

from codegate.database.models.analysis import AnalyzerRun, CodeMetric, Finding
from codegate.database.models.pull_request import PullRequest, PullRequestFile
from codegate.engines.risk.components import (
    calculate_change_surface_risk,
    calculate_complexity_risk,
    calculate_security_risk,
    calculate_sensitive_path_risk,
)
from codegate.engines.risk.config import RISK_CALCULATION_VERSION, get_risk_level
from codegate.engines.risk.schemas import RiskScoreResult


class RiskScoreEngine:
    
    @staticmethod
    def calculate(
        pr: PullRequest,
        pr_files: List[PullRequestFile],
        findings: List[Finding], 
        metrics: List[CodeMetric],
        analyzer_runs: List[AnalyzerRun]
    ) -> RiskScoreResult:
        
        components = [
            calculate_security_risk(findings, analyzer_runs),
            calculate_change_surface_risk(pr),
            calculate_sensitive_path_risk(pr_files),
            calculate_complexity_risk(metrics, analyzer_runs)
        ]
        
        available_weight = sum(c.canonical_weight for c in components if c.included)
        missing_dimensions = [c.name for c in components if not c.included]
        
        # Calculate overall risk
        overall_risk = 0.0
        
        if available_weight > 0:
            weighted_sum = sum((c.risk or 0.0) * c.canonical_weight for c in components if c.included)
            overall_risk = weighted_sum / available_weight
            
            # Populate effective_weights
            for c in components:
                if c.included:
                    c.effective_weight = c.canonical_weight / available_weight
        else:
            overall_risk = 0.0
            
        overall_risk = round(overall_risk, 2)
        risk_level = get_risk_level(overall_risk)
        
        # Collect flags
        flags_set = set()
        for c in components:
            for flag in c.flags:
                flags_set.add(flag)
                
        is_complete = len(missing_dimensions) == 0
        
        return RiskScoreResult(
            overall_risk=overall_risk,
            risk_level=risk_level,
            is_complete=is_complete,
            available_weight=available_weight,
            missing_dimensions=missing_dimensions,
            components=components,
            flags=sorted(list(flags_set)),
            calculation_version=RISK_CALCULATION_VERSION
        )
