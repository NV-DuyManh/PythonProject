from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Tuple

from sqlalchemy import and_, case, desc, func, select
from sqlalchemy.orm import Session

from codegate.database.models import (
    AnalysisRun,
    CoverageReport,
    Finding,
    PolicyDecision,
    PolicyEvaluation,
    PullRequest,
    QualityScore,
    Repository,
    RiskScore,
    Status,
    TestRun,
    Trigger,
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
        repositories_total = db.scalar(repo_stmt) or 0

        # 2. PR counts
        pr_stmt = select(func.count(PullRequest.id)).where(func.lower(PullRequest.state) == "open")
        if repository_id:
            pr_stmt = pr_stmt.where(PullRequest.repository_id == repository_id)
        open_pull_requests = db.scalar(pr_stmt) or 0
        
        pr_total_stmt = select(func.count(PullRequest.id))
        if repository_id:
            pr_total_stmt = pr_total_stmt.where(PullRequest.repository_id == repository_id)
        pr_total_stmt = self._apply_date_filter(pr_total_stmt, from_date, to_date, PullRequest.created_at)
        pull_requests_total = db.scalar(pr_total_stmt) or 0

        # 3. Latest Analysis Runs Subquery
        # We only want the latest analysis run per PR for current distributions and status
        latest_ar_subq = select(
            AnalysisRun.pull_request_id,
            func.max(AnalysisRun.created_at).label("max_created_at")
        ).group_by(AnalysisRun.pull_request_id).subquery()
        
        # Base query for all analyses (historical trends)
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

        # Helper to join the latest analysis
        def _join_latest_ar(stmt, target_model, ar_join_needed=True):
            if ar_join_needed:
                stmt = stmt.join(AnalysisRun, AnalysisRun.id == target_model.analysis_run_id)
            stmt = stmt.join(
                latest_ar_subq,
                and_(
                    AnalysisRun.pull_request_id == latest_ar_subq.c.pull_request_id,
                    AnalysisRun.created_at == latest_ar_subq.c.max_created_at
                )
            )
            if repository_id:
                stmt = stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
            stmt = self._apply_date_filter(stmt, from_date, to_date, AnalysisRun.created_at)
            return stmt

        # Quality
        q_stmt = select(func.avg(QualityScore.overall_score))
        q_stmt = _join_latest_ar(q_stmt, QualityScore)
        average_quality = db.scalar(q_stmt)

        q_dist_stmt = select(QualityScore.grade, func.count(QualityScore.id)).group_by(QualityScore.grade)
        q_dist_stmt = _join_latest_ar(q_dist_stmt, QualityScore)
        q_dist_res = db.execute(q_dist_stmt).fetchall()
        quality_grade_distribution = {grade: count for grade, count in q_dist_res if grade}

        # Risk
        r_stmt = select(func.avg(RiskScore.overall_risk))
        r_stmt = _join_latest_ar(r_stmt, RiskScore)
        average_risk = db.scalar(r_stmt)
        
        r_dist_stmt = select(RiskScore.risk_level, func.count(RiskScore.id)).group_by(RiskScore.risk_level)
        r_dist_stmt = _join_latest_ar(r_dist_stmt, RiskScore)
        r_dist_res = db.execute(r_dist_stmt).fetchall()
        risk_level_distribution = {level: count for level, count in r_dist_res if level}

        # Policy
        p_stmt = select(
            func.sum(case((PolicyEvaluation.decision == PolicyDecision.PASS, 1), else_=0)),
            func.sum(case((PolicyEvaluation.decision == PolicyDecision.WARNING, 1), else_=0)),
            func.sum(case((PolicyEvaluation.decision == PolicyDecision.BLOCK, 1), else_=0)),
            func.count(PolicyEvaluation.id)
        )
        p_stmt = _join_latest_ar(p_stmt, PolicyEvaluation)
        p_res = db.execute(p_stmt).fetchone()
        p_pass, p_warn, p_block, p_total = p_res if p_res else (0, 0, 0, 0)
        p_pass, p_warn, p_block, p_total = p_pass or 0, p_warn or 0, p_block or 0, p_total or 0
        
        policy_decision_distribution = {
            "PASS": p_pass,
            "WARNING": p_warn,
            "BLOCK": p_block
        }

        # Testing
        t_stmt = select(
            func.sum(case((TestRun.test_outcome == "PASSED", 1), else_=0)),
            func.sum(case((TestRun.test_outcome == "FAILED", 1), else_=0)),
            func.count(TestRun.id)
        )
        t_stmt = _join_latest_ar(t_stmt, TestRun)
        t_res = db.execute(t_stmt).fetchone()
        t_pass, t_fail, t_total = t_res if t_res else (0, 0, 0)
        t_pass, t_fail, t_total = t_pass or 0, t_fail or 0, t_total or 0

        # Coverage
        c_stmt = select(
            func.avg(CoverageReport.line_coverage),
            func.avg(CoverageReport.changed_line_coverage)
        )
        # Note: CoverageReport joins to TestRun which joins to AnalysisRun
        c_stmt = c_stmt.join(TestRun, TestRun.id == CoverageReport.test_run_id).join(AnalysisRun, AnalysisRun.id == TestRun.analysis_run_id)
        c_stmt = c_stmt.join(
            latest_ar_subq,
            and_(
                AnalysisRun.pull_request_id == latest_ar_subq.c.pull_request_id,
                AnalysisRun.created_at == latest_ar_subq.c.max_created_at
            )
        )
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
        f_stmt = _join_latest_ar(f_stmt, Finding)
        f_res = db.execute(f_stmt).fetchone()
        f_crit, f_high, f_high_sec = f_res if f_res else (0, 0, 0)
        f_crit, f_high, f_high_sec = f_crit or 0, f_high or 0, f_high_sec or 0

        from codegate.database.models.reviewer import ReviewerRecommendation
        rev_stmt = select(func.count(ReviewerRecommendation.id))
        rev_stmt = _join_latest_ar(rev_stmt, ReviewerRecommendation)
        rev_total = db.scalar(rev_stmt) or 0
        
        # Historical Trends (Uses all data, grouped by date)
        # Example for quality/risk trend:
        # SELECT date(AnalysisRun.created_at), AVG(QualityScore.overall_score), AVG(RiskScore.overall_risk)
        trend_stmt = select(
            func.date(AnalysisRun.created_at).label("date_str"),
            func.avg(QualityScore.overall_score).label("avg_quality"),
            func.avg(RiskScore.overall_risk).label("avg_risk")
        ).join(QualityScore, QualityScore.analysis_run_id == AnalysisRun.id, isouter=True) \
         .join(RiskScore, RiskScore.analysis_run_id == AnalysisRun.id, isouter=True)
         
        if repository_id:
            trend_stmt = trend_stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        trend_stmt = self._apply_date_filter(trend_stmt, from_date, to_date, AnalysisRun.created_at)
        trend_stmt = trend_stmt.group_by(func.date(AnalysisRun.created_at)).order_by(func.date(AnalysisRun.created_at))
        
        trend_res = db.execute(trend_stmt).fetchall()
        
        quality_trend = []
        risk_trend = []
        for date_str, avg_q, avg_r in trend_res:
            if avg_q is not None:
                quality_trend.append({"date": str(date_str), "value": avg_q})
            if avg_r is not None:
                risk_trend.append({"date": str(date_str), "value": avg_r})

        # Coverage trend
        cov_trend_stmt = select(
            func.date(AnalysisRun.created_at).label("date_str"),
            func.avg(CoverageReport.changed_line_coverage).label("avg_changed_cov")
        ).join(TestRun, TestRun.analysis_run_id == AnalysisRun.id) \
         .join(CoverageReport, CoverageReport.test_run_id == TestRun.id)
        
        if repository_id:
            cov_trend_stmt = cov_trend_stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        cov_trend_stmt = self._apply_date_filter(cov_trend_stmt, from_date, to_date, AnalysisRun.created_at)
        cov_trend_stmt = cov_trend_stmt.group_by(func.date(AnalysisRun.created_at)).order_by(func.date(AnalysisRun.created_at))
        
        cov_trend_res = db.execute(cov_trend_stmt).fetchall()
        changed_coverage_trend = []
        for date_str, avg_cc in cov_trend_res:
            if avg_cc is not None:
                changed_coverage_trend.append({"date": str(date_str), "value": avg_cc})
                
        # Policy trend
        pol_trend_stmt = select(
            func.date(AnalysisRun.created_at).label("date_str"),
            func.sum(case((PolicyEvaluation.decision == PolicyDecision.PASS, 1), else_=0)),
            func.sum(case((PolicyEvaluation.decision == PolicyDecision.WARNING, 1), else_=0)),
            func.sum(case((PolicyEvaluation.decision == PolicyDecision.BLOCK, 1), else_=0))
        ).join(PolicyEvaluation, PolicyEvaluation.analysis_run_id == AnalysisRun.id)
        
        if repository_id:
            pol_trend_stmt = pol_trend_stmt.join(PullRequest, PullRequest.id == AnalysisRun.pull_request_id).where(PullRequest.repository_id == repository_id)
        pol_trend_stmt = self._apply_date_filter(pol_trend_stmt, from_date, to_date, AnalysisRun.created_at)
        pol_trend_stmt = pol_trend_stmt.group_by(func.date(AnalysisRun.created_at)).order_by(func.date(AnalysisRun.created_at))
        
        pol_trend_res = db.execute(pol_trend_stmt).fetchall()
        policy_trend = []
        for date_str, pass_c, warn_c, block_c in pol_trend_res:
            policy_trend.append({
                "date": str(date_str),
                "pass_count": pass_c or 0,
                "warning_count": warn_c or 0,
                "block_count": block_c or 0
            })

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
            "policy_pass_rate": (p_pass / p_total * 100) if p_total > 0 else None,
            "policy_warning_rate": (p_warn / p_total * 100) if p_total > 0 else None,
            "policy_block_rate": (p_block / p_total * 100) if p_total > 0 else None,
            "tests_passed_runs": t_pass,
            "tests_failed_runs": t_fail,
            "test_pass_rate": (t_pass / t_total * 100) if t_total > 0 else None,
            "average_line_coverage": avg_cov,
            "average_changed_line_coverage": avg_changed_cov,
            "critical_findings": f_crit,
            "high_findings": f_high,
            "high_security_findings": f_high_sec,
            "reviewer_recommendations_generated": rev_total,
            "quality_trend": quality_trend,
            "risk_trend": risk_trend,
            "changed_coverage_trend": changed_coverage_trend,
            "policy_trend": policy_trend,
            "quality_grade_distribution": quality_grade_distribution,
            "risk_level_distribution": risk_level_distribution,
            "policy_decision_distribution": policy_decision_distribution,
        }

analytics_store = AnalyticsStore()
