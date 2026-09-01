import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from codegate.database.models.analysis import AnalysisRun, Status, Trigger, Finding, CodeMetric, Severity, Source

@pytest.fixture
def quality_test_run(db_session: Session):
    from codegate.database.models.repository import Repository, Provider
    from codegate.database.models.pull_request import PullRequest
    
    # Create Repo first
    repo = Repository(
        name="test-repo",
        owner="test-owner",
        full_name="test-owner/test-repo",
        provider=Provider.GITHUB,
        provider_repository_id="test/test-repo",
        url="https://github.com/test/test-repo",
        workspace_id=1
    )
    db_session.add(repo)
    db_session.commit()
    db_session.refresh(repo)

    # Create PR first
    pr = PullRequest(
        repository_id=repo.id,
        number=1,
        title="Quality PR",
        author_username="testuser",
        source_branch="feat",
        target_branch="main",
        changed_files=1,
        state="OPEN",
        head_sha="qual123",
        base_sha="base123"
    )
    db_session.add(pr)
    db_session.commit()
    db_session.refresh(pr)

    run = AnalysisRun(
        pull_request_id=pr.id,
        head_sha="qual123",
        status=Status.COMPLETED,
        trigger=Trigger.MANUAL
    )
    db_session.add(run)
    db_session.commit()
    db_session.refresh(run)
    
    # Add some findings
    f1 = Finding(analysis_run_id=run.id, source=Source.RUFF, is_changed_file=True, severity=Severity.HIGH, title="H", category="Style", description="test description")
    f2 = Finding(analysis_run_id=run.id, source=Source.BANDIT, is_changed_file=True, severity=Severity.MEDIUM, title="M", category="Sec", description="test description")
    db_session.add_all([f1, f2])
    db_session.commit()
    
    return run

def test_calculate_and_persist_api(client: TestClient, quality_test_run: AnalysisRun):
    # Call recalculate to calculate and persist
    resp = client.post(f"/api/v1/analyses/{quality_test_run.id}/quality/recalculate")
    assert resp.status_code == 200
    data = resp.json()
    
    assert data["analysis_run_id"] == quality_test_run.id
    assert "overall_score" in data
    assert "grade" in data
    assert data["is_complete"] is False
    assert data["available_weight"] > 0
    
    # Now test GET
    resp2 = client.get(f"/api/v1/analyses/{quality_test_run.id}/quality")
    assert resp2.status_code == 200
    data2 = resp2.json()
    
    assert data2["overall_score"] == data["overall_score"]
    
def test_get_quality_not_found(client: TestClient):
    resp = client.get("/api/v1/analyses/99999/quality")
    assert resp.status_code == 404
