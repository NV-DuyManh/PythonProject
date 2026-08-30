from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, select, and_, desc, case

from codegate.database.models import (
    Repository, PullRequest, AnalysisRun, 
    QualityScore, RiskScore, PolicyEvaluation, 
    TestRun, CoverageReport, Finding, Status, Trigger, PolicyDecision
)

class AnalyticsStore:
    def _apply_date_filter(self, stmt: Any, from_date: Optional[datetime], to_date: Optional[datetime], date_column: Any):
        if from_date:
            stmt = stmt.where(date_column >= from_date)
        if to_date:
            stmt = stmt.where(date_column <= to_date)
        return stmt

    def get_overview_kpis(self, db: Session, repository_id: Optional[int] = None, from_date: Optional[datetime] = None, to_date: Optional[datetime] = None):
        # 1. Total Repos
        repo_stmt = select(func.count(Repository.id))
        if repository_id:
            repo_stmt = repo_stmt.where(Repository.id == repository_id)
        # Note: repo creation date isn't filtered, but PRs are. We might just return repo count.
        repositories_total = db.scalar(repo_stmt) or 0

        # 2. PR counts
        pr_stmt = select(func.count(PullRequest.id)).where(PullRequest.state == "open")
        if repository_id:
            pr_stmt = pr_stmt.where(PullRequest.repository_id == repository_id)
        open_pull_requests = db.scalar(pr_stmt) or 0
        
        pr_total_stmt = select(func.count(PullRequest.id))
        if repository_id:
            pr_total_stmt = pr_total_stmt.where(PullRequest.repository_id == repository_id)
        pr_total_stmt = self._apply_date_filter(pr_total_stmt, from_date, to_date, PullRequest.created_at)
        pull_requests_total = db.scalar(pr_total_stmt) or 0

        # 3. Analysis counts
        ar_base = select(AnalysisRun.id)
        if repository_id:
            ar_base = ar_base.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        ar_base = self._apply_date_filter(ar_base, from_date, to_date, AnalysisRun.created_at)
        
        ar_subq = ar_base.subquery()

        analyses_total = db.scalar(select(func.count(ar_subq.c.id))) or 0
        
        comp_stmt = select(func.count(AnalysisRun.id)).where(AnalysisRun.status == Status.COMPLETED)
        if repository_id:
            comp_stmt = comp_stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        comp_stmt = self._apply_date_filter(comp_stmt, from_date, to_date, AnalysisRun.created_at)
        analyses_completed = db.scalar(comp_stmt) or 0
        
        fail_stmt = select(func.count(AnalysisRun.id)).where(AnalysisRun.status == Status.FAILED)
        if repository_id:
            fail_stmt = fail_stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        fail_stmt = self._apply_date_filter(fail_stmt, from_date, to_date, AnalysisRun.created_at)
        analyses_failed = db.scalar(fail_stmt) or 0

        # Quality
        q_stmt = select(func.avg(QualityScore.overall_score))
        q_stmt = q_stmt.join(AnalysisRun, AnalysisRun.id == QualityScore.analysis_run_id)
        if repository_id:
            q_stmt = q_stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        q_stmt = self._apply_date_filter(q_stmt, from_date, to_date, AnalysisRun.created_at)
        average_quality = db.scalar(q_stmt)

        # Risk
        r_stmt = select(func.avg(RiskScore.overall_risk))
        r_stmt = r_stmt.join(AnalysisRun, AnalysisRun.id == RiskScore.analysis_run_id)
        if repository_id:
            r_stmt = r_stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        r_stmt = self._apply_date_filter(r_stmt, from_date, to_date, AnalysisRun.created_at)
        average_risk = db.scalar(r_stmt)

        # Policy
        p_stmt = select(
            func.sum(case((PolicyEvaluation.decision == PolicyDecision.PASS, 1), else_=0)),
            func.sum(case((PolicyEvaluation.decision == PolicyDecision.WARNING, 1), else_=0)),
            func.sum(case((PolicyEvaluation.decision == PolicyDecision.BLOCK, 1), else_=0)),
            func.count(PolicyEvaluation.id)
        )
        p_stmt = p_stmt.join(AnalysisRun, AnalysisRun.id == PolicyEvaluation.analysis_run_id)
        if repository_id:
            p_stmt = p_stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        p_stmt = self._apply_date_filter(p_stmt, from_date, to_date, AnalysisRun.created_at)
        p_res = db.execute(p_stmt).fetchone()
        p_pass, p_warn, p_block, p_total = p_res if p_res else (0, 0, 0, 0)
        p_pass = p_pass or 0
        p_warn = p_warn or 0
        p_block = p_block or 0
        p_total = p_total or 0

        # Testing
        t_stmt = select(
            func.sum(case((TestRun.test_outcome == "PASSED", 1), else_=0)),
            func.sum(case((TestRun.test_outcome == "FAILED", 1), else_=0)),
            func.count(TestRun.id)
        )
        t_stmt = t_stmt.join(AnalysisRun, AnalysisRun.id == TestRun.analysis_run_id)
        if repository_id:
            t_stmt = t_stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        t_stmt = self._apply_date_filter(t_stmt, from_date, to_date, AnalysisRun.created_at)
        t_res = db.execute(t_stmt).fetchone()
        t_pass, t_fail, t_total = t_res if t_res else (0, 0, 0)
        t_pass = t_pass or 0
        t_fail = t_fail or 0
        t_total = t_total or 0

        # Coverage
        c_stmt = select(
            func.avg(CoverageReport.line_coverage),
            func.avg(CoverageReport.changed_line_coverage)
        )
        c_stmt = c_stmt.join(TestRun, TestRun.id == CoverageReport.test_run_id).join(AnalysisRun, AnalysisRun.id == TestRun.analysis_run_id)
        if repository_id:
            c_stmt = c_stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        c_stmt = self._apply_date_filter(c_stmt, from_date, to_date, AnalysisRun.created_at)
        c_res = db.execute(c_stmt).fetchone()
        avg_cov, avg_changed_cov = c_res if c_res else (None, None)

        # Findings
        f_stmt = select(
            func.sum(case((Finding.severity == "CRITICAL", 1), else_=0)),
            func.sum(case((Finding.severity == "HIGH", 1), else_=0)),
            func.sum(case((and_(Finding.severity == "HIGH", Finding.category == "SECURITY"), 1), else_=0)),
        )
        f_stmt = f_stmt.join(AnalysisRun, AnalysisRun.id == Finding.analysis_run_id)
        if repository_id:
            f_stmt = f_stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        f_stmt = self._apply_date_filter(f_stmt, from_date, to_date, AnalysisRun.created_at)
        f_res = db.execute(f_stmt).fetchone()
        f_crit, f_high, f_high_sec = f_res if f_res else (0, 0, 0)

        # Reviewers - just count AnalysisRun where reviewers were generated? The prompt doesn't specify deeply for overview. 
        # But we don't have a reviewer table connected directly, ReviewerRecommendation has analysis_run_id.
        from codegate.database.models.reviewer import ReviewerRecommendation
        rev_stmt = select(func.count(ReviewerRecommendation.id))
        rev_stmt = rev_stmt.join(AnalysisRun, AnalysisRun.id == ReviewerRecommendation.analysis_run_id)
        if repository_id:
            rev_stmt = rev_stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        rev_stmt = self._apply_date_filter(rev_stmt, from_date, to_date, AnalysisRun.created_at)
        rev_total = db.scalar(rev_stmt) or 0

        return {
            "repositories_total": repositories_total,
            "pull_requests_total": pull_requests_total,
            "open_pull_requests": open_pull_requests,
            "analyses_total": analyses_total,
            "analyses_completed": analyses_completed,
            "analyses_failed": analyses_failed,
            "average_quality_score": average_quality,
            "average_risk_score": average_risk,
            "policy_pass_count": p_pass,
            "policy_warning_count": p_warn,
            "policy_block_count": p_block,
            "policy_pass_rate": p_pass / p_total if p_total > 0 else None,
            "policy_warning_rate": p_warn / p_total if p_total > 0 else None,
            "policy_block_rate": p_block / p_total if p_total > 0 else None,
            "tests_passed_runs": t_pass,
            "tests_failed_runs": t_fail,
            "test_pass_rate": t_pass / t_total if t_total > 0 else None,
            "average_line_coverage": avg_cov,
            "average_changed_line_coverage": avg_changed_cov,
            "critical_findings": f_crit or 0,
            "high_findings": f_high or 0,
            "high_security_findings": f_high_sec or 0,
            "reviewer_recommendations_generated": rev_total,
            "quality_trend": [],
            "risk_trend": [],
            "changed_coverage_trend": [],
            "policy_trend": [],
        }

analytics_store = AnalyticsStore()
