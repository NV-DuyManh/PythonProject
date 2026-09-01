import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from codegate.api.main import app
from codegate.config.settings import settings
from codegate.database.models import User, AuthSession

@pytest.fixture
def override_github_config(monkeypatch):
    monkeypatch.setattr(settings, "GITHUB_OAUTH_CLIENT_ID", "test_id")
    monkeypatch.setattr(settings, "GITHUB_OAUTH_CLIENT_SECRET", "test_secret")

def test_login_redirects_and_sets_cookie(override_github_config, client):
    response = client.get("/api/v1/auth/github/login", follow_redirects=False)
    assert response.status_code == 307
    assert "https://github.com/login/oauth/authorize" in response.headers["location"]
    
    # Verify oauth_state cookie is set
    cookies = response.headers.get("set-cookie")
    assert "oauth_state=" in cookies
    assert "HttpOnly" in cookies

def test_login_fails_if_unconfigured(monkeypatch, client):
    monkeypatch.setattr(settings, "GITHUB_OAUTH_CLIENT_ID", None)
    response = client.get("/api/v1/auth/github/login")
    assert response.status_code == 500
    assert "not configured" in response.json()["detail"]

def test_callback_missing_state(client):
    response = client.get("/api/v1/auth/github/callback?code=123")
    assert response.status_code == 400
    assert "Invalid or missing OAuth state" in response.json()["detail"]

def test_callback_mismatched_state(client):
    client.cookies.set("oauth_state", "real_state")
    response = client.get("/api/v1/auth/github/callback?code=123&state=fake_state")
    assert response.status_code == 400
    assert "Invalid or missing OAuth state" in response.json()["detail"]

def test_get_me_unauthenticated(db_session):
    """Use a raw client without get_current_user override so /auth/me returns 401."""
    from codegate.api.main import app
    from codegate.api.dependencies import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as raw_client:
        response = raw_client.get("/api/v1/auth/me")
    app.dependency_overrides.clear()
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_logout_clears_cookie(client):
    # Setup dummy session cookie
    client.cookies.set("codegate_session", "dummy_token")
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    # Cookie should be cleared
    cookies = response.headers.get("set-cookie")
    assert "codegate_session=;" in cookies or 'Max-Age=0' in cookies or 'expires' in cookies.lower()

# Mocking Github API for full flow test
from unittest.mock import AsyncMock, patch
from codegate.services.github_auth import GitHubUser

@pytest.fixture
def mock_github_auth():
    with patch("codegate.api.routers.auth.get_github_access_token", new_callable=AsyncMock) as mock_token, \
         patch("codegate.api.routers.auth.get_github_user", new_callable=AsyncMock) as mock_user:
        mock_token.return_value = "fake_access_token"
        yield mock_user

def test_github_login_twice_reuses_user(override_github_config, mock_github_auth, client, db_session):
    # Setup mock user
    mock_github_auth.return_value = GitHubUser(id=123456, login="test-user")
    
    # First login
    client.cookies.set("oauth_state", "state123")
    res1 = client.get("/api/v1/auth/github/callback?code=code123&state=state123", follow_redirects=False)
    assert res1.status_code == 307
    
    initial_user_count = db_session.query(User).count()
    
    # Second login
    client.cookies.set("oauth_state", "state456")
    res2 = client.get("/api/v1/auth/github/callback?code=code456&state=state456", follow_redirects=False)
    assert res2.status_code == 307
    
    final_user_count = db_session.query(User).count()
    assert initial_user_count == final_user_count
    
    # Ensure it's the correct user
    user = db_session.query(User).filter(User.provider_user_id == "123456").first()
    assert user is not None
    assert user.username == "test-user"

def test_github_username_rename_updates_user(override_github_config, mock_github_auth, client, db_session):
    # First login with old name
    mock_github_auth.return_value = GitHubUser(id=789012, login="old-name")
    client.cookies.set("oauth_state", "state1")
    client.get("/api/v1/auth/github/callback?code=code1&state=state1", follow_redirects=False)
    
    user1 = db_session.query(User).filter(User.provider_user_id == "789012").first()
    assert user1.username == "old-name"
    
    # Second login with new name but same numeric ID
    mock_github_auth.return_value = GitHubUser(id=789012, login="new-name")
    client.cookies.set("oauth_state", "state2")
    client.get("/api/v1/auth/github/callback?code=code2&state=state2", follow_redirects=False)
    
    user2 = db_session.query(User).filter(User.provider_user_id == "789012").first()
    
    # User count should be exactly the same, but username updated
    assert user1.id == user2.id
    assert user2.username == "new-name"

