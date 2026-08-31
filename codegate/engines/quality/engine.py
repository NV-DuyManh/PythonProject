from typing import List, Optional

from codegate.database.models.analysis import CodeMetric, Finding
from codegate.engines.quality.components import (
    calculate_ai_review,
    calculate_code_quality,
    calculate_complexity,
    calculate_maintainability,
    calculate_security,
    calculate_testing,
)
from codegate.engines.quality.config import CALCULATION_VERSION, get_grade
from codegate.engines.quality.schemas import QualityScoreResult


class QualityScoreEngine:
    
    @staticmethod
    def calculate(findings: List[Finding], metrics: List[CodeMetric], testing_score: Optional[float] = None) -> QualityScoreResult:
        components = [
            calculate_code_quality(findings),
            calculate_security(findings),
            calculate_complexity(metrics, findings),
            calculate_maintainability(),
            calculate_testing(testing_score),
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
