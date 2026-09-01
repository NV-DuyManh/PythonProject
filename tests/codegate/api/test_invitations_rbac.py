import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

from codegate.api.main import app
from codegate.api.dependencies import get_db, get_current_user
from codegate.database.models import User, Team, TeamMember, Role

client = TestClient(app)

import uuid

def setup_workspace(db_session: Session, actor_role: Role):
    uid = str(uuid.uuid4())
    # Create actor
    actor = User(provider="GITHUB", provider_user_id=f"actor_{uid}", username=f"actor_{uid}", email=f"actor_{uid}@example.com")
    db_session.add(actor)
    db_session.commit()
    db_session.refresh(actor)
    
    # Create workspace
    team = Team(name=f"Test Workspace {uid}")
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)
    
    actor.active_workspace_id = team.id
    db_session.commit()
    
    # Create member
    member = TeamMember(team_id=team.id, user_id=actor.id, role=actor_role)
    db_session.add(member)
    db_session.commit()
    
    return actor, team

@pytest.fixture
def mock_auth(monkeypatch, db_session):
    def _mock_auth(user: User):
        app.dependency_overrides[get_current_user] = lambda: user
        app.dependency_overrides[get_db] = lambda: db_session
    
    yield _mock_auth
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_db, None)

@pytest.mark.parametrize("actor_role,target_role,expected_status", [
    (Role.ADMIN, Role.ADMIN, 200),
    (Role.ADMIN, Role.MAINTAINER, 200),
    (Role.ADMIN, Role.REVIEWER, 200),
    (Role.ADMIN, Role.DEVELOPER, 200),
    
    (Role.MAINTAINER, Role.MAINTAINER, 200),
    (Role.MAINTAINER, Role.REVIEWER, 200),
    (Role.MAINTAINER, Role.DEVELOPER, 200),
    (Role.MAINTAINER, Role.ADMIN, 403), # Blocked
    
    (Role.REVIEWER, Role.ADMIN, 403), # Blocked
    (Role.REVIEWER, Role.REVIEWER, 403), # Blocked completely from endpoint
    
    (Role.DEVELOPER, Role.ADMIN, 403),
    (Role.DEVELOPER, Role.DEVELOPER, 403),
])
def test_create_invitation_rbac(db_session: Session, mock_auth, actor_role, target_role, expected_status):
    actor, team = setup_workspace(db_session, actor_role)
    mock_auth(actor)
    
    payload = {
        "role": target_role.value,
        "invitee_email": "target@example.com"
    }
    
    response = client.post("/api/v1/workspaces/active/invitations", json=payload)
    assert response.status_code == expected_status

def test_role_change_rbac(db_session: Session, mock_auth):
    actor, team = setup_workspace(db_session, Role.MAINTAINER)
    mock_auth(actor)
    
    target_uid = str(uuid.uuid4())
    target = User(provider="GITHUB", provider_user_id=f"target_{target_uid}", username=f"target_{target_uid}", email=f"t_{target_uid}@example.com")
    db_session.add(target)
    db_session.commit()
    
    member = TeamMember(team_id=team.id, user_id=target.id, role=Role.DEVELOPER)
    db_session.add(member)
    db_session.commit()
    
    # Maintainer cannot upgrade to ADMIN because of can_grant_role
    payload = {"role": Role.ADMIN.value}
    response = client.patch(f"/api/v1/workspaces/active/members/{target.id}", json=payload)
    assert response.status_code == 403
    
    # Let's test admin upgrading someone to admin
    actor2, team2 = setup_workspace(db_session, Role.ADMIN)
    mock_auth(actor2)
    
    target_uid2 = str(uuid.uuid4())
    target2 = User(provider="GITHUB", provider_user_id=f"target2_{target_uid2}", username=f"target2_{target_uid2}")
    db_session.add(target2)
    db_session.commit()
    member2 = TeamMember(team_id=team2.id, user_id=target2.id, role=Role.DEVELOPER)
    db_session.add(member2)
    db_session.commit()
    
    payload2 = {"role": Role.ADMIN.value}
    response2 = client.patch(f"/api/v1/workspaces/active/members/{target2.id}", json=payload2)
    assert response2.status_code == 200

