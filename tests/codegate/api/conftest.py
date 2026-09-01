import pytest
from fastapi.testclient import TestClient
from codegate.api.main import app
from codegate.api.dependencies import get_db, get_current_workspace, get_current_user
from codegate.database.models import Team, User, TeamMember
from codegate.database.models.team import Role

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Create a mock workspace if it doesn't exist
    mock_team = db_session.get(Team, 1)
    if not mock_team:
        mock_team = Team(id=1, name="Test Workspace", description="Mock workspace for tests")
        db_session.add(mock_team)
        db_session.commit()

    # Create a mock user with membership so require_workspace_permission works
    mock_user = User(
        id=1,
        provider="github",
        provider_user_id="test-fixture-user",
        username="testuser",
        email="test@fixture.local",
        is_active=True,
        active_workspace_id=mock_team.id,
    )
    db_session.merge(mock_user)
    db_session.commit()

    existing_member = db_session.query(TeamMember).filter_by(
        team_id=mock_team.id, user_id=mock_user.id
    ).first()
    if not existing_member:
        member = TeamMember(team_id=mock_team.id, user_id=mock_user.id, role=Role.ADMIN)
        db_session.add(member)
        db_session.commit()

    def override_get_current_workspace():
        return mock_team

    def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_workspace] = override_get_current_workspace
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

