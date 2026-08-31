from datetime import datetime
from typing import Optional

from sqlalchemy import and_, case, func, select
from sqlalchemy.orm import Session

from codegate.database.models import (
    AnalysisRun,
    CoverageReport,
    Finding,
    PolicyEvaluation,
    PullRequest,
    QualityScore,
    Repository,
    RiskScore,
    Status,
    TestRun,
)
from codegate.repositories.analytics_store import analytics_store
from codegate.schemas.analytics import (
    AnalyticsFilter,
    FindingsAnalytics,
    PolicyAnalytics,
    QualityAnalytics,
    ReviewerAnalytics,
    RiskAnalytics,
    TestingAnalytics,
)


class AnalyticsService:
    def get_quality_analytics(
        self, db: Session, repository_id: Optional[int], from_date: Optional[datetime], to_date: Optional[datetime]
    ) -> QualityAnalytics:
        # Base query for Quality Scores
        stmt = select(func.avg(QualityScore.overall_score), func.count(QualityScore.id))
        stmt = stmt.join(AnalysisRun, AnalysisRun.id == QualityScore.analysis_run_id)
        
        if repository_id:
            stmt = stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
            
        stmt = analytics_store._apply_date_filter(stmt, from_date, to_date, AnalysisRun.created_at)
        
        res = db.execute(stmt).fetchone()
        avg_q, total_q = res if res else (None, 0)
        
        # Missing count = total completed analyses - total quality scores
        ar_stmt = select(func.count(AnalysisRun.id)).where(AnalysisRun.status == Status.COMPLETED)
        if repository_id:
            ar_stmt = ar_stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        ar_stmt = analytics_store._apply_date_filter(ar_stmt, from_date, to_date, AnalysisRun.created_at)
        total_analyses = db.scalar(ar_stmt) or 0
        
        missing = total_analyses - (total_q or 0)
        if missing < 0:
            missing = 0
            
        # Distribution
        dist_stmt = select(QualityScore.grade, func.count(QualityScore.id)).group_by(QualityScore.grade)
        dist_stmt = dist_stmt.join(AnalysisRun, AnalysisRun.id == QualityScore.analysis_run_id)
        if repository_id:
            dist_stmt = dist_stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        dist_stmt = analytics_store._apply_date_filter(dist_stmt, from_date, to_date, AnalysisRun.created_at)
        
        dist_res = db.execute(dist_stmt).all()
        dist = {grade: count for grade, count in dist_res}
        
        return QualityAnalytics(
            average_quality=avg_q,
            missing_count=missing,
            grade_distribution=dist,
            trend=[]
        )
        
    def get_risk_analytics(
        self, db: Session, repository_id: Optional[int], from_date: Optional[datetime], to_date: Optional[datetime]
    ) -> RiskAnalytics:
        stmt = select(func.avg(RiskScore.overall_risk), func.count(RiskScore.id))
        stmt = stmt.join(AnalysisRun, AnalysisRun.id == RiskScore.analysis_run_id)
        
        if repository_id:
            stmt = stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
            
        stmt = analytics_store._apply_date_filter(stmt, from_date, to_date, AnalysisRun.created_at)
        
        res = db.execute(stmt).fetchone()
        avg_r, total_r = res if res else (None, 0)
        
        ar_stmt = select(func.count(AnalysisRun.id)).where(AnalysisRun.status == Status.COMPLETED)
        if repository_id:
            ar_stmt = ar_stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        ar_stmt = analytics_store._apply_date_filter(ar_stmt, from_date, to_date, AnalysisRun.created_at)
        total_analyses = db.scalar(ar_stmt) or 0
        
        missing = total_analyses - (total_r or 0)
        if missing < 0:
            missing = 0
            
        dist_stmt = select(RiskScore.risk_level, func.count(RiskScore.id)).group_by(RiskScore.risk_level)
        dist_stmt = dist_stmt.join(AnalysisRun, AnalysisRun.id == RiskScore.analysis_run_id)
        if repository_id:
            dist_stmt = dist_stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        dist_stmt = analytics_store._apply_date_filter(dist_stmt, from_date, to_date, AnalysisRun.created_at)
        
        dist_res = db.execute(dist_stmt).all()
        dist = {level: count for level, count in dist_res}
        
        return RiskAnalytics(
            average_risk=avg_r,
            missing_count=missing,
            level_distribution=dist,
            trend=[],
            high_risk_pr_count=dist.get("HIGH", 0),
            critical_risk_pr_count=dist.get("CRITICAL", 0)
        )

    def get_policy_analytics(
        self, db: Session, repository_id: Optional[int], from_date: Optional[datetime], to_date: Optional[datetime]
    ) -> PolicyAnalytics:
        stmt = select(
            func.sum(case((PolicyEvaluation.decision == "PASS", 1), else_=0)),
            func.sum(case((PolicyEvaluation.decision == "WARNING", 1), else_=0)),
            func.sum(case((PolicyEvaluation.decision == "BLOCK", 1), else_=0)),
            func.count(PolicyEvaluation.id)
        )
        stmt = stmt.join(AnalysisRun, AnalysisRun.id == PolicyEvaluation.analysis_run_id)
        if repository_id:
            stmt = stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        stmt = analytics_store._apply_date_filter(stmt, from_date, to_date, AnalysisRun.created_at)
        
        res = db.execute(stmt).fetchone()
        p_pass, p_warn, p_block, p_total = res if res else (0, 0, 0, 0)
        p_pass = p_pass or 0
        p_warn = p_warn or 0
        p_block = p_block or 0
        p_total = p_total or 0
        
        return PolicyAnalytics(
            pass_count=p_pass,
            warning_count=p_warn,
            block_count=p_block,
            pass_rate=p_pass / p_total if p_total > 0 else None,
            warning_rate=p_warn / p_total if p_total > 0 else None,
            block_rate=p_block / p_total if p_total > 0 else None,
            trend=[],
            top_blocking_rules=[],
            top_warning_rules=[]
        )

    def get_findings_analytics(
        self, db: Session, repository_id: Optional[int], from_date: Optional[datetime], to_date: Optional[datetime], changed_only: bool = False
    ) -> FindingsAnalytics:
        stmt = select(
            func.count(Finding.id),
            func.sum(case((Finding.is_changed_file == True, 1), else_=0))
        )
        stmt = stmt.join(AnalysisRun, AnalysisRun.id == Finding.analysis_run_id)
        if repository_id:
            stmt = stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        stmt = analytics_store._apply_date_filter(stmt, from_date, to_date, AnalysisRun.created_at)
        
        if changed_only:
            stmt = stmt.where(Finding.is_changed_file == True)
            
        res = db.execute(stmt).fetchone()
        total, changed = res if res else (0, 0)
        total = total or 0
        changed = changed or 0
        
        # Distributions
        dist_stmt = select(Finding.severity, func.count(Finding.id)).group_by(Finding.severity)
        dist_stmt = dist_stmt.join(AnalysisRun, AnalysisRun.id == Finding.analysis_run_id)
        if repository_id:
            dist_stmt = dist_stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        dist_stmt = analytics_store._apply_date_filter(dist_stmt, from_date, to_date, AnalysisRun.created_at)
        if changed_only:
            dist_stmt = dist_stmt.where(Finding.is_changed_file == True)
            
        dist_res = db.execute(dist_stmt).all()
        sev_dist = {sev: count for sev, count in dist_res}
        
        return FindingsAnalytics(
            total_findings=total,
            changed_code_findings=changed,
            historical_findings=total - changed,
            severity_distribution=sev_dist,
            category_distribution={},
            source_distribution={},
            top_rules=[],
            top_affected_files=[]
        )

    def get_testing_analytics(
        self, db: Session, repository_id: Optional[int], from_date: Optional[datetime], to_date: Optional[datetime]
    ) -> TestingAnalytics:
        stmt = select(
            func.sum(case((TestRun.test_outcome == "PASSED", 1), else_=0)),
            func.sum(case((TestRun.test_outcome == "FAILED", 1), else_=0)),
            func.sum(case((TestRun.test_outcome == "UNKNOWN", 1), else_=0)),
            func.avg(TestRun.duration_ms),
            func.count(TestRun.id)
        )
        stmt = stmt.join(AnalysisRun, AnalysisRun.id == TestRun.analysis_run_id)
        if repository_id:
            stmt = stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        stmt = analytics_store._apply_date_filter(stmt, from_date, to_date, AnalysisRun.created_at)
        
        res = db.execute(stmt).fetchone()
        t_pass, t_fail, t_unk, t_dur, t_total = res if res else (0, 0, 0, None, 0)
        t_pass = t_pass or 0
        t_fail = t_fail or 0
        t_unk = t_unk or 0
        t_total = t_total or 0
        
        # Coverage
        c_stmt = select(
            func.avg(CoverageReport.line_coverage),
            func.avg(CoverageReport.changed_line_coverage),
            func.count(CoverageReport.id)
        )
        c_stmt = c_stmt.join(TestRun, TestRun.id == CoverageReport.test_run_id).join(AnalysisRun, AnalysisRun.id == TestRun.analysis_run_id)
        if repository_id:
            c_stmt = c_stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        c_stmt = analytics_store._apply_date_filter(c_stmt, from_date, to_date, AnalysisRun.created_at)
        
        c_res = db.execute(c_stmt).fetchone()
        c_line, c_changed, c_total = c_res if c_res else (None, None, 0)
        c_total = c_total or 0
        
        missing = t_total - c_total
        if missing < 0:
            missing = 0
            
        return TestingAnalytics(
            test_runs=t_total,
            passed_runs=t_pass,
            failed_runs=t_fail,
            unknown_runs=t_unk,
            test_pass_rate=t_pass / (t_pass + t_fail) if (t_pass + t_fail) > 0 else None, # pass rate based on executed result denominator
            average_duration=t_dur / 1000.0 if t_dur else None,
            average_line_coverage=c_line,
            average_changed_code_coverage=c_changed,
            missing_count=missing,
            coverage_trend=[],
            changed_coverage_distribution={}
        )

    def get_reviewer_analytics(
        self, db: Session, repository_id: Optional[int], from_date: Optional[datetime], to_date: Optional[datetime]
    ) -> ReviewerAnalytics:
        # Placeholder
        return ReviewerAnalytics(
            recommendations_generated=0,
            no_suitable_reviewer_count=0,
            partial_recommendation_count=0,
            top_recommended_reviewers=[],
            average_recommendation_score=None,
            reviewer_recommendation_frequency={}
        )

analytics_service = AnalyticsService()
