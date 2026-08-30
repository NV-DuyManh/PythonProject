from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel


class AnalyticsFilter(BaseModel):
    repository_id: Optional[int] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None


class QualityAnalytics(BaseModel):
    average_quality: Optional[float]
    missing_count: int
    grade_distribution: Any
    trend: List[Any]


class RiskAnalytics(BaseModel):
    average_risk: Optional[float]
    missing_count: int
    level_distribution: Any
    trend: List[Any]
    high_risk_pr_count: int
    critical_risk_pr_count: int


class PolicyAnalytics(BaseModel):
    pass_count: int
    warning_count: int
    block_count: int
    pass_rate: Optional[float]
    warning_rate: Optional[float]
    block_rate: Optional[float]
    trend: List[Any]
    top_blocking_rules: List[Any]
    top_warning_rules: List[Any]


class FindingsAnalytics(BaseModel):
    total_findings: int
    changed_code_findings: int
    historical_findings: int
    severity_distribution: Any
    category_distribution: Any
    source_distribution: Any
    top_rules: List[Any]
    top_affected_files: List[Any]


class TestingAnalytics(BaseModel):
    test_runs: int
    passed_runs: int
    failed_runs: int
    unknown_runs: int
    test_pass_rate: Optional[float]
    average_duration: Optional[float]
    average_line_coverage: Optional[float]
    average_changed_code_coverage: Optional[float]
    missing_count: int
    coverage_trend: List[Any]
    changed_coverage_distribution: Any


class ReviewerAnalytics(BaseModel):
    recommendations_generated: int
    no_suitable_reviewer_count: int
    partial_recommendation_count: int
    top_recommended_reviewers: List[Any]
    average_recommendation_score: Optional[float]
    reviewer_recommendation_frequency: Any
