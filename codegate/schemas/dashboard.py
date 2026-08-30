from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class DashboardOverviewTrendPoint(BaseModel):
    date: str
    value: Optional[float] = None
    pass_count: Optional[int] = None
    warning_count: Optional[int] = None
    block_count: Optional[int] = None


class DashboardOverviewResponse(BaseModel):
    repositories_total: int
    
    pull_requests_total: int
    open_pull_requests: int
    
    analyses_total: int
    analyses_completed: int
    analyses_failed: int
    
    average_quality_score: Optional[float]
    average_risk_score: Optional[float]
    
    policy_pass_count: int
    policy_warning_count: int
    policy_block_count: int
    
    policy_pass_rate: Optional[float]
    policy_warning_rate: Optional[float]
    policy_block_rate: Optional[float]
    
    tests_passed_runs: int
    tests_failed_runs: int
    test_pass_rate: Optional[float]
    
    average_line_coverage: Optional[float]
    average_changed_line_coverage: Optional[float]
    
    critical_findings: int
    high_findings: int
    high_security_findings: int
    
    reviewer_recommendations_generated: int
    
    quality_trend: List[DashboardOverviewTrendPoint]
    risk_trend: List[DashboardOverviewTrendPoint]
    changed_coverage_trend: List[DashboardOverviewTrendPoint]
    policy_trend: List[DashboardOverviewTrendPoint]


class RepositoryDashboardItem(BaseModel):
    repository_id: int
    name: str
    provider: str
    active: bool
    
    open_pr_count: int
    analysis_count: int
    
    average_quality: Optional[float]
    average_risk: Optional[float]
    
    policy_pass_count: int
    policy_warning_count: int
    policy_block_count: int
    block_rate: Optional[float]
    
    test_pass_rate: Optional[float]
    average_changed_coverage: Optional[float]
    
    critical_findings: int
    
    last_analysis_at: Optional[datetime]


class PRDashboardItem(BaseModel):
    pull_request_id: int
    repository: str
    number: int
    title: str
    author: str
    state: str
    
    head_sha: str
    base_sha: str
    
    latest_analysis_id: Optional[int]
    analysis_status: Optional[str]
    
    quality_score: Optional[float]
    quality_grade: Optional[str]
    
    risk_score: Optional[float]
    risk_level: Optional[str]
    
    policy_decision: Optional[str]
    
    test_outcome: Optional[str]
    changed_line_coverage: Optional[float]
    
    critical_findings: int
    high_findings: int
    
    recommended_reviewers_count: int
    
    updated_at: datetime


class PRDetailComponent(BaseModel):
    id: int
    number: int
    title: str
    author: str
    state: str
    repository: str
    base_sha: str
    head_sha: str


class AnalysisDetailComponent(BaseModel):
    analysis_id: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime]


class QualityDetailComponent(BaseModel):
    overall_score: float
    grade: str
    is_complete: bool
    available_weight: float
    missing_dimensions: Optional[Any]
    components: Optional[Any]  # Deprecated? Replaced by breakdown
    breakdown: Any


class RiskDetailComponent(BaseModel):
    overall_risk: float
    risk_level: str
    is_complete: bool
    available_weight: float
    missing_dimensions: Optional[Any]
    components: Optional[Any]
    flags: Optional[Any]
    breakdown: Any


class PolicyDetailComponent(BaseModel):
    decision: str
    policy_revision: int
    engine_version: str
    passed_rules: int
    warning_rules: int
    blocked_rules: int
    flags: Optional[Any]
    breakdown: Any


class TestsDetailComponent(BaseModel):
    execution_status: str
    test_outcome: Optional[str]
    total: int
    passed: int
    failed: int
    errors: int
    skipped: int
    duration: Optional[float]


class CoverageDetailComponent(BaseModel):
    line_coverage: Optional[float]
    branch_coverage: Optional[float]
    changed_line_coverage: Optional[float]
    changed_total_lines: Optional[int]
    changed_covered_lines: Optional[int]
    changed_missing_lines: Optional[int]
    is_complete: bool


class FindingsDetailComponent(BaseModel):
    total: int
    critical: int
    high: int
    medium: int
    low: int
    info: int
    by_category: Any
    top_findings: List[Any]


class ReviewerDetailComponent(BaseModel):
    status: str
    is_complete: bool
    recommended_reviewers: List[Any]


class PullRequestDashboardDetail(BaseModel):
    pr: PRDetailComponent
    analysis: Optional[AnalysisDetailComponent]
    quality: Optional[QualityDetailComponent]
    risk: Optional[RiskDetailComponent]
    policy: Optional[PolicyDetailComponent]
    tests: Optional[TestsDetailComponent]
    coverage: Optional[CoverageDetailComponent]
    findings: Optional[FindingsDetailComponent]
    reviewer_recommendation: Optional[ReviewerDetailComponent]


class RepositoryDetailComponent(BaseModel):
    repository_id: int
    name: str
    provider: str
    active: bool

class RepositoryDetailResponse(BaseModel):
    repository: RepositoryDetailComponent
    health: Any
    policy_summary: Any
    test_config_summary: Any
    reviewer_config_summary: Any
    recent_prs: List[PRDashboardItem]
    quality_distribution: Any
    risk_distribution: Any
    policy_distribution: Any
    testing_summary: Any
    coverage_summary: Any
    finding_summary: Any
    top_security_rules: List[Any]
    sensitive_path_activity: List[Any]
    recent_analyses: List[Any]
