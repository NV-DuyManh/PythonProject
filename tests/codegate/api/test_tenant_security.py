import pytest
from fastapi.testclient import TestClient

from codegate.api.main import app
from codegate.api.dependencies import get_current_workspace, get_db
from codegate.database.models import (
    Team, Repository, PullRequest, AnalysisRun, Finding, 
    QualityScore, RiskScore, PolicyEvaluation, QualityPolicy, TestRun as DBTestRun, CoverageReport, 
    ReviewerRecommendation, ReviewerRecommendationConfig, GitHubConnection
)

def setup_tenants(db_session):
    workspace_a = Team(id=101, name="Workspace A")
    workspace_b = Team(id=102, name="Workspace B")
    workspace_null = Team(id=103, name="Workspace Null")
    db_session.add_all([workspace_a, workspace_b, workspace_null])
    db_session.commit()
    
    # GitHub Connection for A
    gh_conn_a = GitHubConnection(id=101, provider="github", account_login="org-a", installation_id="inst-a", workspace_id=101)
    db_session.add(gh_conn_a)
    db_session.commit()
    
    # Create resources in A
    repo_a = Repository(id=101, name="repo_a", owner="org", full_name="org/repo_a", provider="github", url="https://github.com/org/repo_a", workspace_id=101)
    repo_null = Repository(id=102, name="repo_null", owner="org", full_name="org/repo_null", provider="github", url="https://github.com/org/repo_null", workspace_id=None)
    db_session.add_all([repo_a, repo_null])
    db_session.commit()
    
    pr_a = PullRequest(id=101, repository_id=101, provider_pr_id="pr-1", number=1, title="PR A", author_username="user1", state="open", source_branch="feat", target_branch="main", head_sha="head", base_sha="base")
    pr_null = PullRequest(id=102, repository_id=102, provider_pr_id="pr-2", number=2, title="PR Null", author_username="user1", state="open", source_branch="feat", target_branch="main", head_sha="head", base_sha="base")
    db_session.add_all([pr_a, pr_null])
    db_session.commit()
    
    ar_a = AnalysisRun(id=101, pull_request_id=101, status="COMPLETED", head_sha="abc1234", trigger="manual")
    ar_null = AnalysisRun(id=102, pull_request_id=102, status="COMPLETED", head_sha="abc1234", trigger="manual")
    db_session.add_all([ar_a, ar_null])
    db_session.commit()
    
    finding_a = Finding(id=101, analysis_run_id=101, source="AI", category="security", severity="HIGH", file_path="a.py", start_line=1, end_line=1, title="test", description="desc")
    db_session.add(finding_a)
    db_session.commit()

    quality_a = QualityScore(id=101, analysis_run_id=101, overall_score=90.0, grade="A", available_weight=1.0, breakdown_json={}, calculation_version="1.0")
    db_session.add(quality_a)
    
    risk_a = RiskScore(id=101, analysis_run_id=101, overall_risk=10.0, risk_level="LOW", available_weight=1.0, breakdown_json={}, calculation_version="1.0")
    db_session.add(risk_a)
    
    quality_policy_a = QualityPolicy(id=101, repository_id=101, name="Standard", policy_engine_version="1.0", revision=1)
    db_session.add(quality_policy_a)
    db_session.commit()
    
    policy_a = PolicyEvaluation(id=101, analysis_run_id=101, policy_id=101, policy_engine_version="1.0", policy_revision=1, evaluation_status="COMPLETED")
    db_session.add(policy_a)
    
    test_run_a = DBTestRun(id=101, analysis_run_id=101, runner_version="1.0", framework="pytest", executor_type="local", execution_status="COMPLETED", test_outcome="PASSED", tests_total=1, tests_passed=1)
    db_session.add(test_run_a)
    db_session.commit()
    
    cov_a = CoverageReport(id=101, test_run_id=101, coverage_version="1.0")
    db_session.add(cov_a)
    
    rev_config_a = ReviewerRecommendationConfig(id=101, repository_id=101)
    db_session.add(rev_config_a)
    db_session.commit()
    
    rev_a = ReviewerRecommendation(id=101, analysis_run_id=101, config_id=101, engine_version="1.0", config_revision=1, status="COMPLETED")
    db_session.add(rev_a)
    
    db_session.commit()

    return workspace_a, workspace_b

@pytest.fixture
def client_workspace_b(db_session):
    workspace_a, workspace_b = setup_tenants(db_session)

    # Create a user in workspace B with correct role
    from codegate.database.models import User, TeamMember
    from codegate.database.models.team import Role
    user_b = User(
        id=201,
        provider="github",
        provider_user_id="test-user-b",
        username="testuser_b",
        email="b@test.local",
        is_active=True,
        active_workspace_id=workspace_b.id,
    )
    db_session.merge(user_b)
    db_session.commit()

    existing_member = db_session.query(TeamMember).filter_by(
        team_id=workspace_b.id, user_id=user_b.id
    ).first()
    if not existing_member:
        member_b = TeamMember(team_id=workspace_b.id, user_id=user_b.id, role=Role.ADMIN)
        db_session.add(member_b)
        db_session.commit()

    def override_get_db():
        yield db_session

    def override_get_workspace_b():
        return workspace_b

    def override_get_current_user():
        return user_b

    from codegate.api.dependencies import get_current_user
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_workspace] = override_get_workspace_b
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

@pytest.fixture
def unauth_client(db_session):
    setup_tenants(db_session)
    
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
        
    app.dependency_overrides.clear()

def test_idor_repository(client_workspace_b):
    response = client_workspace_b.get("/api/v1/repositories/101")
    assert response.status_code == 404
    
def test_idor_repository_null(client_workspace_b):
    response = client_workspace_b.get("/api/v1/repositories/102")
    assert response.status_code == 404

def test_idor_pull_request(client_workspace_b):
    response = client_workspace_b.get("/api/v1/pull-requests/101")
    assert response.status_code == 404
    
def test_idor_pull_request_null(client_workspace_b):
    response = client_workspace_b.get("/api/v1/pull-requests/102")
    assert response.status_code == 404

def test_idor_analysis(client_workspace_b):
    response = client_workspace_b.get("/api/v1/analyses/101")
    assert response.status_code == 404
    
def test_idor_analysis_null(client_workspace_b):
    response = client_workspace_b.get("/api/v1/analyses/102")
    assert response.status_code == 404
    
def test_idor_findings(client_workspace_b):
    response = client_workspace_b.get("/api/v1/analyses/101/findings")
    assert response.status_code == 404
    
def test_idor_quality(client_workspace_b):
    response = client_workspace_b.get("/api/v1/analyses/101/quality")
    assert response.status_code == 404

def test_idor_risk(client_workspace_b):
    response = client_workspace_b.get("/api/v1/analyses/101/risk")
    assert response.status_code == 404

def test_idor_policy(client_workspace_b):
    response = client_workspace_b.get("/api/v1/analyses/101/policy")
    assert response.status_code == 404
    
def test_idor_test_run(client_workspace_b):
    response = client_workspace_b.get("/api/v1/analyses/101/tests")
    assert response.status_code == 404

def test_idor_coverage(client_workspace_b):
    response = client_workspace_b.get("/api/v1/analyses/101/coverage")
    assert response.status_code == 404

def test_idor_reviewer(client_workspace_b):
    response = client_workspace_b.get("/api/v1/analyses/101/reviewers")
    assert response.status_code == 404

def test_idor_metrics(client_workspace_b):
    response = client_workspace_b.get("/api/v1/analyses/101/metrics")
    assert response.status_code == 404

def test_idor_testing_config(client_workspace_b):
    response = client_workspace_b.get("/api/v1/repositories/101/test-config")
    assert response.status_code == 404
    
def test_idor_github_connections(client_workspace_b):
    # Trying to list should only return B's, so 0 for B
    response = client_workspace_b.get("/api/v1/integrations/github/connections")
    assert response.status_code == 200
    assert len(response.json()) == 0
    
def test_idor_dashboard_overview(client_workspace_b):
    response = client_workspace_b.get("/api/v1/dashboard/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["pull_requests_total"] == 0

def test_idor_analytics(client_workspace_b):
    response = client_workspace_b.get("/api/v1/analytics/quality?repository_id=101")
    data = response.json()
    assert data["average_quality"] is None
    assert data["missing_count"] == 0

def test_malicious_workspace_body(client_workspace_b):
    # We test creating a repo in B, passing workspace_id=101 (A). The backend should ignore it and use B (102).
    # Assuming repository creation endpoint accepts body
    response = client_workspace_b.post("/api/v1/repositories", json={
        "name": "malicious",
        "owner": "org",
        "provider": "github",
        "url": "https://github.com/org/malicious",
        "workspace_id": 101, # Try to set to A
        "github_connection_id": None
    })
    
    if response.status_code == 200:
        data = response.json()
        # Verify that workspace_id is B (102), not A (101), or it was blocked
        assert data["workspace_id"] == 102

def test_anonymous_domain_apis(unauth_client):
    endpoints = [
        "/api/v1/repositories/101",
        "/api/v1/pull-requests/101",
        "/api/v1/analyses/101",
        "/api/v1/analyses/101/findings",
        "/api/v1/analyses/101/quality",
        "/api/v1/analyses/101/risk",
        "/api/v1/analyses/101/policy",
        "/api/v1/dashboard/overview",
        "/api/v1/analytics/quality",
        "/api/v1/integrations/github/connections"
    ]
    for endpoint in endpoints:
        response = unauth_client.get(endpoint)
        assert response.status_code == 401
