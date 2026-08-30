import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from codegate.api.main import app
from codegate.database.models import AnalysisRun, PullRequest, Finding, Source, Severity, Status, QualityScore, RiskScore, Trigger
from codegate.database.models.pull_request import State
from codegate.engines.risk.engine import RiskScoreEngine

client = TestClient(app)

def test_risk_api_get_404(db_session: Session):
    from codegate.api.dependencies import get_db
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.get("/api/v1/analyses/9999/risk")
    app.dependency_overrides.clear()
    assert response.status_code == 404

def test_risk_api_recalculate_and_get(db_session: Session):
    # Setup Data
    pr = PullRequest(repository_id=1, provider_pr_id="1", number=1, state=State.OPEN, author_username="testuser", source_branch="src", target_branch="tgt", head_sha="sha", title="test", additions=100, deletions=10, changed_files=2)
    db_session.add(pr)
    db_session.commit()
    
    run = AnalysisRun(pull_request_id=pr.id, head_sha=pr.head_sha, status=Status.COMPLETED, trigger=Trigger.MANUAL)
    db_session.add(run)
    db_session.commit()
    
    finding = Finding(analysis_run_id=run.id, source=Source.BANDIT, category="Security", severity=Severity.HIGH, title="High", description="desc", is_changed_file=True)
    db_session.add(finding)
    db_session.commit()
    from codegate.api.dependencies import get_db
    app.dependency_overrides[get_db] = lambda: db_session
    
    response = client.post(f"/api/v1/analyses/{run.id}/risk/recalculate")
    assert response.status_code == 200
    
    # Get Risk
    response = client.get(f"/api/v1/analyses/{run.id}/risk")
    assert response.status_code == 200
    data = response.json()
    assert data["analysis_run_id"] == run.id
    assert data["security_risk"] == 70.0
    
    # 2. GET
    response_get = client.get(f"/api/v1/analyses/{run.id}/risk")
    assert response_get.status_code == 200
    assert response_get.json() == data
    
    # 3. Unique verification
    client.post(f"/api/v1/analyses/{run.id}/risk/recalculate")
    client.post(f"/api/v1/analyses/{run.id}/risk/recalculate")
    
    app.dependency_overrides.clear()
    
    scores = db_session.query(RiskScore).filter_by(analysis_run_id=run.id).all()
    assert len(scores) == 1

def test_risk_api_partial(db_session: Session):
    from codegate.database.models.pull_request import State
    pr = PullRequest(repository_id=1, provider_pr_id="2", number=2, state=State.OPEN, author_username="testuser", source_branch="src", target_branch="tgt", head_sha="sha", title="test", additions=100, deletions=10, changed_files=2)
    db_session.add(pr)
    db_session.commit()
    
    run = AnalysisRun(pull_request_id=pr.id, head_sha=pr.head_sha, status=Status.COMPLETED, trigger=Trigger.MANUAL)
    db_session.add(run)
    db_session.commit()
    from codegate.api.dependencies import get_db
    app.dependency_overrides[get_db] = lambda: db_session
    
    response = client.post(f"/api/v1/analyses/{run.id}/risk/recalculate")
    data = response.json()
    assert response.status_code == 200, f"Response was {response.status_code}: {data}"
    assert data.get("complexity_risk") is None
    assert data["is_complete"] is False
    assert "complexity" in data["missing_dimensions"]
    
    app.dependency_overrides.clear()
