import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from codegate.database.models import AnalysisRun, PullRequest, Finding, Source, Severity, Status, QualityScore, RiskScore, Trigger
from codegate.database.models.pull_request import State
from codegate.database.models.repository import Repository, Provider
from codegate.engines.risk.engine import RiskScoreEngine


def _ensure_repo(db_session: Session) -> Repository:
    """Ensure a workspace-scoped repository exists for risk tests."""
    repo = db_session.query(Repository).filter_by(id=1).first()
    if not repo:
        repo = Repository(
            id=1,
            name="risk-test-repo",
            owner="test-owner",
            full_name="test-owner/risk-test-repo",
            provider=Provider.GITHUB,
            url="https://github.com/test/risk-test-repo",
            workspace_id=1
        )
        db_session.add(repo)
        db_session.commit()
    return repo


def test_risk_api_get_404(client: TestClient):
    response = client.get("/api/v1/analyses/9999/risk")
    assert response.status_code == 404


def test_risk_api_recalculate_and_get(client: TestClient, db_session: Session):
    _ensure_repo(db_session)

    pr = PullRequest(repository_id=1, provider_pr_id="1", number=1, state=State.OPEN, author_username="testuser", source_branch="src", target_branch="tgt", head_sha="sha", title="test", additions=100, deletions=10, changed_files=2)
    db_session.add(pr)
    db_session.commit()

    run = AnalysisRun(pull_request_id=pr.id, head_sha=pr.head_sha, status=Status.COMPLETED, trigger=Trigger.MANUAL)
    db_session.add(run)
    db_session.commit()

    finding = Finding(analysis_run_id=run.id, source=Source.BANDIT, category="Security", severity=Severity.HIGH, title="High", description="desc", is_changed_file=True)
    db_session.add(finding)
    db_session.commit()

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

    scores = db_session.query(RiskScore).filter_by(analysis_run_id=run.id).all()
    assert len(scores) == 1


def test_risk_api_partial(client: TestClient, db_session: Session):
    _ensure_repo(db_session)

    pr = PullRequest(repository_id=1, provider_pr_id="2", number=2, state=State.OPEN, author_username="testuser", source_branch="src", target_branch="tgt", head_sha="sha2", title="test", additions=100, deletions=10, changed_files=2)
    db_session.add(pr)
    db_session.commit()

    run = AnalysisRun(pull_request_id=pr.id, head_sha=pr.head_sha, status=Status.COMPLETED, trigger=Trigger.MANUAL)
    db_session.add(run)
    db_session.commit()

    response = client.post(f"/api/v1/analyses/{run.id}/risk/recalculate")
    data = response.json()
    assert response.status_code == 200, f"Response was {response.status_code}: {data}"
    assert data.get("complexity_risk") is None
    assert data["is_complete"] is False
    assert "complexity" in data["missing_dimensions"]
