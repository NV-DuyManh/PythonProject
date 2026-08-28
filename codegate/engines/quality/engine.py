from typing import List
from codegate.database.models.analysis import Finding, CodeMetric
from codegate.engines.quality.schemas import QualityScoreResult
from codegate.engines.quality.config import CALCULATION_VERSION, get_grade
from codegate.engines.quality.components import (
    calculate_code_quality,
    calculate_security,
    calculate_complexity,
    calculate_maintainability,
    calculate_testing,
    calculate_ai_review,
)

class QualityScoreEngine:
    
    @staticmethod
    def calculate(findings: List[Finding], metrics: List[CodeMetric]) -> QualityScoreResult:
        components = [
            calculate_code_quality(findings),
            calculate_security(findings),
            calculate_complexity(metrics, findings),
            calculate_maintainability(),
            calculate_testing(),
            calculate_ai_review(findings)
        ]
        
        available_weight = sum(c.canonical_weight for c in components if c.included)
        
        if available_weight <= 0:
            return QualityScoreResult(
                overall_score=0.0,
                grade="F",
                is_complete=False,
                available_weight=0.0,
                missing_dimensions=[c.name for c in components if not c.included],
                components=components,
                calculation_version=CALCULATION_VERSION
            )
            
        weighted_score_sum = sum((c.score or 0.0) * c.canonical_weight for c in components if c.included)
        
        overall_score = weighted_score_sum / available_weight
        
        # Round overall score to 2 decimal places to match float precision
        overall_score = round(overall_score, 2)
        
        grade = get_grade(overall_score)
        
        missing_dimensions = [c.name for c in components if not c.included]
        is_complete = len(missing_dimensions) == 0
        
        return QualityScoreResult(
            overall_score=overall_score,
            grade=grade,
            is_complete=is_complete,
            available_weight=available_weight,
            missing_dimensions=missing_dimensions,
            components=components,
            calculation_version=CALCULATION_VERSION
        )
