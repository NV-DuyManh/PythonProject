from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc

from codegate.database.models import (
    Repository, PullRequest, AnalysisRun, 
    QualityScore, RiskScore, PolicyEvaluation, 
    TestRun, CoverageReport, Finding, Status
)
from codegate.schemas.dashboard import (
    DashboardOverviewResponse, RepositoryDashboardItem, PRDashboardItem,
    PullRequestDashboardDetail, PRDetailComponent, AnalysisDetailComponent,
    QualityDetailComponent, RiskDetailComponent, PolicyDetailComponent,
    TestsDetailComponent, CoverageDetailComponent, FindingsDetailComponent,
    ReviewerDetailComponent, DashboardOverviewTrendPoint
)
from codegate.repositories.analytics_store import analytics_store

class DashboardService:
    def get_overview(
        self, 
        db: Session, 
        repository_id: Optional[int] = None, 
        from_date: Optional[datetime] = None, 
        to_date: Optional[datetime] = None
    ) -> DashboardOverviewResponse:
        kpis = analytics_store.get_overview_kpis(db, repository_id, from_date, to_date)
        return DashboardOverviewResponse(**kpis)

    def get_repositories(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[RepositoryDashboardItem]:
        # Simple repository fetch for now. We can join metrics if needed.
        # But to avoid N+1 we should fetch them grouped.
        stmt = select(Repository)
        if search:
            stmt = stmt.where(Repository.name.ilike(f"%{search}%"))
            
        repos = db.scalars(stmt).all()
        # Fallback to fetching basic info since the prompt expects many fields.
        items = []
        for repo in repos:
            # We fetch individually for now to pass the tests. We can optimize later if time permits.
            kpis = analytics_store.get_overview_kpis(db, repository_id=repo.id, from_date=from_date, to_date=to_date)
            items.append(
                RepositoryDashboardItem(
                    repository_id=repo.id,
                    name=repo.name,
                    provider=repo.provider,
                    active=repo.is_active if hasattr(repo, 'is_active') else True,
                    open_pr_count=kpis["open_pull_requests"],
                    analysis_count=kpis["analyses_total"],
                    average_quality=kpis["average_quality_score"],
                    average_risk=kpis["average_risk_score"],
                    policy_pass_count=kpis["policy_pass_count"],
                    policy_warning_count=kpis["policy_warning_count"],
                    policy_block_count=kpis["policy_block_count"],
                    block_rate=kpis["policy_block_rate"],
                    test_pass_rate=kpis["test_pass_rate"],
                    average_changed_coverage=kpis["average_changed_line_coverage"],
                    critical_findings=kpis["critical_findings"],
                    last_analysis_at=None # TODO fetch last analysis
                )
            )
            
        # In-memory sorting for now
        def sort_key(x):
            val = getattr(x, sort_by)
            return val if val is not None else (0 if isinstance(val, (int, float)) else "")
            
        items.sort(key=sort_key, reverse=(sort_order == "desc"))
        
        # Paginate
        start = (page - 1) * page_size
        return items[start:start + page_size]

    def get_pull_requests(
        self,
        db: Session,
        repository_id: Optional[int] = None,
        status: Optional[str] = None,
        policy_decision: Optional[str] = None,
        risk_level: Optional[str] = None,
        quality_grade: Optional[str] = None,
        author: Optional[str] = None,
        search: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> List[PRDashboardItem]:
        # Very simplified for now. In a real app we'd build a complex join.
        stmt = select(PullRequest)
        if repository_id:
            stmt = stmt.where(PullRequest.repository_id == repository_id)
        if author:
            stmt = stmt.where(PullRequest.author == author)
        if search:
            stmt = stmt.where(PullRequest.title.ilike(f"%{search}%"))
        
        # Date filtering
        if from_date:
            stmt = stmt.where(PullRequest.updated_at >= from_date)
        if to_date:
            stmt = stmt.where(PullRequest.updated_at <= to_date)
            
        stmt = stmt.order_by(desc(PullRequest.updated_at))
        
        prs = db.scalars(stmt).all()
        
        items = []
        for pr in prs:
            repo = db.get(Repository, pr.repository_id)
            # Find latest analysis
            ar_stmt = select(AnalysisRun).where(AnalysisRun.pull_request_id == pr.id).order_by(desc(AnalysisRun.created_at)).limit(1)
            ar = db.scalar(ar_stmt)
            
            # This logic mimics the detailed aggregation, but limits fields.
            item = PRDashboardItem(
                pull_request_id=pr.id,
                repository=repo.name if repo else "",
                number=pr.number,
                title=pr.title,
                description=pr.description,
                author=pr.author_username,
                source_branch=pr.source_branch,
                state=pr.state,
                head_sha=(pr.head_sha or "") if hasattr(pr, 'head_sha') else "",
                base_sha=(pr.base_sha or "") if hasattr(pr, 'base_sha') else "",
                latest_analysis_id=ar.id if ar else None,
                analysis_status=getattr(ar.status, 'value', ar.status) if ar else None,
                quality_score=None,
                quality_grade=None,
                risk_score=None,
                risk_level=None,
                policy_decision=None,
                test_outcome=None,
                changed_line_coverage=None,
                critical_findings=0,
                high_findings=0,
                recommended_reviewers_count=0,
                updated_at=pr.updated_at
            )
            
            if ar:
                quality = db.scalar(select(QualityScore).where(QualityScore.analysis_run_id == ar.id))
                if quality:
                    item.quality_score = quality.overall_score
                    item.quality_grade = quality.grade
                    
                risk = db.scalar(select(RiskScore).where(RiskScore.analysis_run_id == ar.id))
                if risk:
                    item.risk_score = risk.overall_risk
                    item.risk_level = risk.risk_level
                    
                policy = db.scalar(select(PolicyEvaluation).where(PolicyEvaluation.analysis_run_id == ar.id))
                if policy:
                    item.policy_decision = getattr(policy.decision, 'value', policy.decision) if policy.decision else None
                    
                test = db.scalar(select(TestRun).where(TestRun.analysis_run_id == ar.id))
                if test:
                    item.test_outcome = test.test_outcome
                    cov = db.scalar(select(CoverageReport).where(CoverageReport.test_run_id == test.id))
                    if cov:
                        item.changed_line_coverage = cov.changed_line_coverage
                        
                # Count findings
                item.critical_findings = db.scalar(select(func.count(Finding.id)).where(Finding.analysis_run_id == ar.id, Finding.severity == "CRITICAL")) or 0
                item.high_findings = db.scalar(select(func.count(Finding.id)).where(Finding.analysis_run_id == ar.id, Finding.severity == "HIGH")) or 0
                
                # Filter locally to support policy/risk filters since we fetched full PRs.
                if status and pr.state != status:
                    continue
                if policy_decision and item.policy_decision != policy_decision:
                    continue
                if risk_level and item.risk_level != risk_level:
                    continue
                if quality_grade and item.quality_grade != quality_grade:
                    continue

            items.append(item)
            
        start = (page - 1) * page_size
        return items[start:start + page_size]

    def get_pull_request_detail(
        self,
        db: Session,
        pull_request_id: int,
        analysis_id: Optional[int] = None
    ) -> Optional[PullRequestDashboardDetail]:
        pr = db.get(PullRequest, pull_request_id)
        if not pr:
            return None
            
        repo = db.get(Repository, pr.repository_id)
        
        # Base PR component
        pr_comp = PRDetailComponent(
            id=pr.id,
            number=pr.number,
            title=pr.title,
            description=pr.description,
            author=pr.author_username,
            source_branch=pr.source_branch,
            state=pr.state,
            repository=repo.name if repo else "",
            base_sha=(pr.base_sha or "") if hasattr(pr, 'base_sha') else "",
            head_sha=(pr.head_sha or "") if hasattr(pr, 'head_sha') else "",
        )
        
        # Target specific analysis, or latest
        stmt = select(AnalysisRun).where(AnalysisRun.pull_request_id == pr.id)
        if analysis_id:
            stmt = stmt.where(AnalysisRun.id == analysis_id)
        else:
            stmt = stmt.order_by(desc(AnalysisRun.created_at))
            
        ar = db.scalar(stmt.limit(1))
        
        if not ar:
            return PullRequestDashboardDetail(pr=pr_comp)
            
        # Extract components safely
        quality = db.scalar(select(QualityScore).where(QualityScore.analysis_run_id == ar.id))
        risk = db.scalar(select(RiskScore).where(RiskScore.analysis_run_id == ar.id))
        policy = db.scalar(select(PolicyEvaluation).where(PolicyEvaluation.analysis_run_id == ar.id))
        test = db.scalar(select(TestRun).where(TestRun.analysis_run_id == ar.id))
        cov = db.scalar(select(CoverageReport).where(CoverageReport.test_run_id == test.id)) if test else None
        
        # Compile detail components
        q_comp = None
        if quality:
            q_comp = QualityDetailComponent(
                overall_score=quality.overall_score,
                grade=quality.grade,
                is_complete=quality.is_complete,
                available_weight=quality.available_weight,
                missing_dimensions=quality.missing_dimensions,
                components=quality.breakdown_json,
                breakdown=quality.breakdown_json
            )
            
        r_comp = None
        if risk:
            r_comp = RiskDetailComponent(
                overall_risk=risk.overall_risk,
                risk_level=risk.risk_level,
                is_complete=risk.is_complete,
                available_weight=risk.available_weight,
                missing_dimensions=risk.missing_dimensions,
                components=risk.breakdown_json,
                flags=risk.breakdown_json,
                breakdown=risk.breakdown_json
            )
            
        p_comp = None
        if policy:
            p_comp = PolicyDetailComponent(
                decision=getattr(policy.decision, 'value', policy.decision) if policy.decision else "",
                policy_revision=policy.policy_revision,
                engine_version=policy.policy_engine_version,
                passed_rules=policy.passed_rules_count or 0,
                warning_rules=policy.warning_rules_count or 0,
                blocked_rules=policy.blocked_rules_count or 0,
                flags=policy.flags_json,
                breakdown=policy.breakdown_json
            )
            
        t_comp = None
        if test:
            t_comp = TestsDetailComponent(
                execution_status=test.execution_status,
                test_outcome=test.test_outcome,
                total=test.tests_total or 0,
                passed=test.tests_passed or 0,
                failed=test.tests_failed or 0,
                errors=test.tests_errors or 0,
                skipped=test.tests_skipped or 0,
                duration=test.duration_ms / 1000.0 if test.duration_ms else None
            )
            
        c_comp = None
        if cov:
            c_comp = CoverageDetailComponent(
                line_coverage=cov.line_coverage,
                branch_coverage=cov.branch_coverage,
                changed_line_coverage=cov.changed_line_coverage,
                changed_total_lines=cov.changed_total_lines,
                changed_covered_lines=cov.changed_covered_lines,
                changed_missing_lines=cov.changed_missing_lines,
                is_complete=cov.is_complete
            )
            
        # Findings
        f_total = db.scalar(select(func.count(Finding.id)).where(Finding.analysis_run_id == ar.id)) or 0
        f_crit = db.scalar(select(func.count(Finding.id)).where(Finding.analysis_run_id == ar.id, Finding.severity == "CRITICAL")) or 0
        f_high = db.scalar(select(func.count(Finding.id)).where(Finding.analysis_run_id == ar.id, Finding.severity == "HIGH")) or 0
        f_med = db.scalar(select(func.count(Finding.id)).where(Finding.analysis_run_id == ar.id, Finding.severity == "MEDIUM")) or 0
        f_low = db.scalar(select(func.count(Finding.id)).where(Finding.analysis_run_id == ar.id, Finding.severity == "LOW")) or 0
        f_info = db.scalar(select(func.count(Finding.id)).where(Finding.analysis_run_id == ar.id, Finding.severity == "INFO")) or 0
        
        f_comp = FindingsDetailComponent(
            total=f_total,
            critical=f_crit,
            high=f_high,
            medium=f_med,
            low=f_low,
            info=f_info,
            by_category={}, # Unimplemented grouping
            top_findings=[] # Unimplemented fetch
        )
            
        return PullRequestDashboardDetail(
            pr=pr_comp,
            analysis=AnalysisDetailComponent(
                analysis_id=ar.id,
                status=ar.status.value,
                created_at=ar.created_at,
                completed_at=ar.completed_at
            ),
            quality=q_comp,
            risk=r_comp,
            policy=p_comp,
            tests=t_comp,
            coverage=c_comp,
            findings=f_comp,
            reviewer_recommendation=None
        )

dashboard_service = DashboardService()
