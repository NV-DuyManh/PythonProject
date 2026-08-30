import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

from codegate.database.models import AnalysisRun, PullRequest, Status, QualityScore, RiskScore, Trigger
from codegate.services.risk_service import risk_service
from codegate.services.quality_service import quality_service
from codegate.services.analysis_orchestrator import AnalysisOrchestrator

def test_risk_persistence(db_session: Session):
    from codegate.database.models.pull_request import State
    pr = PullRequest(repository_id=1, provider_pr_id="100", number=100, state=State.OPEN, author_username="testuser", source_branch="src", target_branch="tgt", head_sha="sha", title="test", additions=100, deletions=10, changed_files=2)
    db_session.add(pr)
    db_session.commit()
    
    run = AnalysisRun(pull_request_id=pr.id, head_sha=pr.head_sha, status=Status.COMPLETED, trigger=Trigger.MANUAL)
    db_session.add(run)
    db_session.commit()
    
    # Calculate
    risk_service.calculate_and_persist(db_session, run.id)
    run_id = run.id
    
    # New session read
    db_session.expunge_all()
    score = db_session.query(RiskScore).filter_by(analysis_run_id=run_id).first()
    
    assert score is not None
    assert score.overall_risk >= 0
    assert score.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert score.is_complete is False
    assert score.calculation_version == "risk-v1"
    assert "components" in score.breakdown_json

def test_risk_quality_independence(db_session: Session):
    from codegate.database.models.pull_request import State
    pr = PullRequest(repository_id=1, provider_pr_id="101", number=101, state=State.OPEN, author_username="testuser", source_branch="src", target_branch="tgt", head_sha="sha", title="test", additions=100, deletions=10, changed_files=2)
    db_session.add(pr)
    db_session.commit()
    
    run = AnalysisRun(pull_request_id=pr.id, head_sha=pr.head_sha, status=Status.COMPLETED, trigger=Trigger.MANUAL)
    db_session.add(run)
    db_session.commit()
    
    risk_service.calculate_and_persist(db_session, run.id)
    r1 = db_session.query(RiskScore).filter_by(analysis_run_id=run.id).first()
    r1_val = r1.overall_risk
    r1_level = r1.risk_level
    
    # Add dummy quality score
    qs = QualityScore(analysis_run_id=run.id, overall_score=100, grade="A", available_weight=1.0, is_complete=True, breakdown_json={}, calculation_version="test")
    db_session.add(qs)
    db_session.commit()
    
    risk_service.calculate_and_persist(db_session, run.id)
    db_session.refresh(r1)
    
    assert r1.overall_risk == r1_val
    assert r1.risk_level == r1_level

@patch("codegate.services.analysis_orchestrator.AnalysisOrchestrator._execute_run")
def test_automatic_pipeline_and_quality_failure(mock_execute, db_session: Session):
    import asyncio
    from codegate.database.models import Status
    from codegate.database.models.pull_request import State
    
    pr = PullRequest(repository_id=1, provider_pr_id="102", number=102, state=State.OPEN, author_username="testuser", source_branch="src", target_branch="tgt", head_sha="sha", title="title", additions=100, deletions=10, changed_files=2)
    db_session.add(pr)
    db_session.commit()
    
    # We mock _execute_run to manually insert what we need and then let orchestrator finish
    async def fake_execute(run, url):
        # We simulate the _execute_run without running CodeGateAdapter
        try:
            quality_service.calculate_and_persist(db_session, run.id)
        except Exception:
            pass
        risk_service.calculate_and_persist(db_session, run.id)
        run.status = Status.COMPLETED
        db_session.commit()
        
    mock_execute.side_effect = fake_execute
    
    orchestrator = AnalysisOrchestrator(db_session)
    run, _ = asyncio.run(orchestrator.trigger_analysis(pr, "url"))
    
    # Verify both calculated
    qs = db_session.query(QualityScore).filter_by(analysis_run_id=run.id).first()
    rs = db_session.query(RiskScore).filter_by(analysis_run_id=run.id).first()
    
    assert qs is not None
    assert rs is not None
    
    # Test Quality Failure Independence
    with patch("codegate.services.quality_service.QualityScoreService.calculate_and_persist", side_effect=Exception("Quality fail")):
        pr2 = PullRequest(repository_id=1, provider_pr_id="103", number=103, state=State.OPEN, author_username="testuser", source_branch="src", target_branch="tgt", head_sha="sha", title="title", additions=100, deletions=10, changed_files=2)
        db_session.add(pr2)
        db_session.commit()
        
        run2, _ = asyncio.run(orchestrator.trigger_analysis(pr2, "url"))
        
        # Quality should be missing
        qs2 = db_session.query(QualityScore).filter_by(analysis_run_id=run2.id).first()
        assert qs2 is None
        
        # Risk should exist
        rs2 = db_session.query(RiskScore).filter_by(analysis_run_id=run2.id).first()
        assert rs2 is not None

@patch("codegate.services.analysis_orchestrator.AnalysisOrchestrator._execute_run")
def test_risk_failure_isolation(mock_execute, db_session: Session):
    import asyncio
    from codegate.database.models import Status
    from codegate.database.models.pull_request import State
    
    pr = PullRequest(repository_id=1, provider_pr_id="104", number=104, state=State.OPEN, author_username="testuser", source_branch="src", target_branch="tgt", head_sha="sha", title="title", additions=100, deletions=10, changed_files=2)
    db_session.add(pr)
    db_session.commit()
    
    async def fake_execute(run, url):
        try:
            quality_service.calculate_and_persist(db_session, run.id)
        except Exception:
            pass
        try:
            risk_service.calculate_and_persist(db_session, run.id)
        except Exception:
            pass
        run.status = Status.COMPLETED
        db_session.commit()
    
    mock_execute.side_effect = fake_execute
    
    orchestrator = AnalysisOrchestrator(db_session)
    
    with patch("codegate.services.risk_service.RiskScoreService.calculate_and_persist", side_effect=Exception("Risk fail")):
        run, _ = asyncio.run(orchestrator.trigger_analysis(pr, "url"))
        
        # Quality should exist
        qs = db_session.query(QualityScore).filter_by(analysis_run_id=run.id).first()
        assert qs is not None
        
        # Run should be COMPLETED despite risk failing
        db_session.refresh(run)
        assert run.status == Status.COMPLETED
