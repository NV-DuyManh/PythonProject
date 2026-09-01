import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
import hashlib

from codegate.api.main import app
from codegate.database.models import Team, User, AuthSession
from codegate.database.models.github import GitHubConnection, GitHubInstallationState
from codegate.config.settings import settings


@pytest.fixture
def test_user_session(db_session: Session):
    user = User(
        provider="github",
        provider_user_id="11111",
        username="testinstalluser",
        email="testinstall@example.com",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    workspace = Team(name="Install Workspace")
    db_session.add(workspace)
    db_session.commit()
    
    user.active_workspace_id = workspace.id
    from codegate.database.models import TeamMember
    from codegate.database.models.team import Role
    member = TeamMember(team_id=workspace.id, user_id=user.id, role=Role.ADMIN)
    db_session.add(member)
    
    auth = AuthSession(
        user_id=user.id,
        token_hash="fakehashinstall",
        expires_at=datetime.now(timezone.utc) + timedelta(days=1)
    )
    db_session.add(auth)
    db_session.commit()
    
    return user, workspace


from codegate.api.dependencies import get_current_user, get_current_workspace, get_db

@pytest.fixture
def auth_client(test_user_session, db_session):
    user, workspace = test_user_session
    client = TestClient(app)
    # override dependencies used in install and connections routes
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_current_workspace] = lambda: workspace
    
    def override_get_db():
        yield db_session
        
    app.dependency_overrides[get_db] = override_get_db
    
    yield client
    app.dependency_overrides.clear()


def test_install_start_flow(auth_client, test_user_session, db_session):
    user, workspace = test_user_session
    
    with patch("codegate.config.settings.settings.GITHUB_APP_SLUG", "test-app-slug"):
        response = auth_client.get("/api/v1/integrations/github/install")
        
        assert response.status_code == 200
        data = response.json()
        assert "install_url" in data
        assert "https://github.com/apps/test-app-slug/installations/new?state=" in data["install_url"]
        
        # Check DB for state
        state_str = data["install_url"].split("state=")[1]
        state_hash = hashlib.sha256(state_str.encode()).hexdigest()
        
        db_state = db_session.query(GitHubInstallationState).filter_by(state_hash=state_hash).first()
        assert db_state is not None
        assert db_state.workspace_id == workspace.id
        assert db_state.user_id == user.id
        assert db_state.consumed_at is None


@patch("codegate.api.routers.github.GitHubAppService.get_installation")
def test_setup_callback_success(mock_get_installation, auth_client, test_user_session, db_session):
    user, workspace = test_user_session
    
    # Pre-insert state
    state_token = "valid_state_token"
    state_hash = hashlib.sha256(state_token.encode()).hexdigest()
    
    state = GitHubInstallationState(
        state_hash=state_hash,
        user_id=user.id,
        workspace_id=workspace.id,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    db_session.add(state)
    db_session.commit()
    
    mock_get_installation.return_value = {
        "account": {"login": "test-org", "type": "Organization"},
        "repository_selection": "all"
    }
    
    response = auth_client.get(f"/api/v1/integrations/github/setup?installation_id=9999&setup_action=install&state={state_token}", follow_redirects=False)
    
    assert response.status_code == 307
    assert "github=connected" in response.headers["location"]
    
    db_session.refresh(state)
    assert state.consumed_at is not None
    
    conn = db_session.query(GitHubConnection).filter_by(installation_id="9999").first()
    assert conn is not None
    assert conn.workspace_id == workspace.id
    assert conn.account_login == "test-org"
    assert conn.account_type == "Organization"
    assert conn.repository_selection == "all"
    assert conn.status == "active"


def test_setup_callback_expired_state(auth_client, test_user_session, db_session):
    user, workspace = test_user_session
    
    state_token = "expired_token"
    state_hash = hashlib.sha256(state_token.encode()).hexdigest()
    
    state = GitHubInstallationState(
        state_hash=state_hash,
        user_id=user.id,
        workspace_id=workspace.id,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=10)
    )
    db_session.add(state)
    db_session.commit()
    
    response = auth_client.get(f"/api/v1/integrations/github/setup?installation_id=9999&setup_action=install&state={state_token}")
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()


@patch("codegate.api.routers.github.GitHubAppService.get_installation")
def test_setup_callback_idempotent(mock_get_installation, auth_client, test_user_session, db_session):
    user, workspace = test_user_session
    
    # Add existing connection
    conn = GitHubConnection(
        provider="github",
        installation_id="1111",
        account_login="old-login",
        workspace_id=workspace.id,
        status="disconnected"
    )
    db_session.add(conn)
    db_session.commit()
    
    state_token = "valid_state_2"
    state_hash = hashlib.sha256(state_token.encode()).hexdigest()
    state = GitHubInstallationState(
        state_hash=state_hash, user_id=user.id, workspace_id=workspace.id, 
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    db_session.add(state)
    db_session.commit()
    
    mock_get_installation.return_value = {
        "account": {"login": "new-login", "type": "User"},
        "repository_selection": "selected"
    }
    
    auth_client.get(f"/api/v1/integrations/github/setup?installation_id=1111&setup_action=install&state={state_token}", follow_redirects=False)
    
    db_session.refresh(conn)
    assert conn.status == "active"
    assert conn.account_login == "new-login"
    assert conn.account_type == "User"


@patch("codegate.api.routers.github.GitHubAppService.get_installation")
def test_setup_callback_cross_workspace_collision(mock_get_installation, auth_client, test_user_session, db_session):
    user, workspace = test_user_session
    
    # Create another workspace and assign connection to it
    other_ws = Team(name="Other WS")
    db_session.add(other_ws)
    db_session.commit()
    
    conn = GitHubConnection(
        provider="github",
        installation_id="2222",
        account_login="org-login",
        workspace_id=other_ws.id
    )
    db_session.add(conn)
    db_session.commit()
    
    state_token = "valid_state_3"
    state_hash = hashlib.sha256(state_token.encode()).hexdigest()
    state = GitHubInstallationState(
        state_hash=state_hash, user_id=user.id, workspace_id=workspace.id, 
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    db_session.add(state)
    db_session.commit()
    
    mock_get_installation.return_value = {"account": {"login": "org-login", "type": "Organization"}}
    
    response = auth_client.get(f"/api/v1/integrations/github/setup?installation_id=2222&setup_action=install&state={state_token}", follow_redirects=False)
    
    assert response.status_code == 400
    assert "already connected to another workspace" in response.json()["detail"]

def test_setup_callback_missing_state(auth_client):
    response = auth_client.get("/api/v1/integrations/github/setup?installation_id=9999&setup_action=install")
    assert response.status_code == 422


def test_setup_callback_invalid_state(auth_client):
    response = auth_client.get("/api/v1/integrations/github/setup?installation_id=9999&setup_action=install&state=random123")
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


@patch("codegate.api.routers.github.GitHubAppService.get_installation")
def test_setup_callback_consumed_state(mock_get_installation, auth_client, test_user_session, db_session):
    user, workspace = test_user_session
    state_token = "consumed_token"
    state_hash = hashlib.sha256(state_token.encode()).hexdigest()
    
    state = GitHubInstallationState(
        state_hash=state_hash,
        user_id=user.id,
        workspace_id=workspace.id,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        consumed_at=datetime.now(timezone.utc) - timedelta(minutes=1)
    )
    db_session.add(state)
    db_session.commit()
    
    response = auth_client.get(f"/api/v1/integrations/github/setup?installation_id=9999&setup_action=install&state={state_token}")
    assert response.status_code == 400
    assert "consumed" in response.json()["detail"].lower()


@patch("codegate.api.routers.github.GitHubAppService.get_installation")
def test_setup_callback_fake_installation(mock_get_installation, auth_client, test_user_session, db_session):
    from fastapi import HTTPException
    
    user, workspace = test_user_session
    state_token = "fake_install_token"
    state_hash = hashlib.sha256(state_token.encode()).hexdigest()
    
    state = GitHubInstallationState(
        state_hash=state_hash,
        user_id=user.id,
        workspace_id=workspace.id,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    db_session.add(state)

def test_setup_callback_missing_state(auth_client):
    response = auth_client.get("/api/v1/integrations/github/setup?installation_id=9999&setup_action=install")
    assert response.status_code == 422


def test_setup_callback_invalid_state(auth_client):
    response = auth_client.get("/api/v1/integrations/github/setup?installation_id=9999&setup_action=install&state=random123")
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


@patch("codegate.api.routers.github.GitHubAppService.get_installation")
def test_setup_callback_consumed_state(mock_get_installation, auth_client, test_user_session, db_session):
    user, workspace = test_user_session
    state_token = "consumed_token"
    state_hash = hashlib.sha256(state_token.encode()).hexdigest()
    
    state = GitHubInstallationState(
        state_hash=state_hash,
        user_id=user.id,
        workspace_id=workspace.id,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        consumed_at=datetime.now(timezone.utc) - timedelta(minutes=1)
    )
    db_session.add(state)
    db_session.commit()
    
    response = auth_client.get(f"/api/v1/integrations/github/setup?installation_id=9999&setup_action=install&state={state_token}")
    assert response.status_code == 400
    assert "consumed" in response.json()["detail"].lower()


@patch("codegate.api.routers.github.GitHubAppService.get_installation")
def test_setup_callback_fake_installation(mock_get_installation, auth_client, test_user_session, db_session):
    from fastapi import HTTPException
    
    user, workspace = test_user_session
    state_token = "fake_install_token"
    state_hash = hashlib.sha256(state_token.encode()).hexdigest()
    
    state = GitHubInstallationState(
        state_hash=state_hash,
        user_id=user.id,
        workspace_id=workspace.id,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    db_session.add(state)
    db_session.commit()
    
    # Mock github service throwing 400 not found (or 404 in underlying)
    mock_get_installation.side_effect = HTTPException(status_code=400, detail="Installation ID 9999 not found or inaccessible.")
    
    response = auth_client.get(f"/api/v1/integrations/github/setup?installation_id=9999&setup_action=install&state={state_token}")
    assert response.status_code == 502
    
    # Ensure no connection is created
    conn = db_session.query(GitHubConnection).filter_by(installation_id="9999").first()
    assert conn is None
