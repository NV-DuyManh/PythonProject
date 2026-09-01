import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from codegate.auth.permissions import Permissions, has_permission, check_last_admin
from codegate.database.models import Base, Team, User
from codegate.database.models.team import Role, TeamMember

# Setup in-memory sqlite db for tests
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_has_permission():
    assert has_permission(Role.ADMIN, Permissions.MEMBERS_INVITE)
    assert has_permission(Role.ADMIN, Permissions.MEMBERS_REMOVE)
    assert not has_permission(Role.DEVELOPER, Permissions.MEMBERS_INVITE)
    assert has_permission(Role.DEVELOPER, Permissions.REPOSITORY_VIEW)
    assert has_permission(Role.REVIEWER, Permissions.POLICY_VIEW)
    assert not has_permission(Role.REVIEWER, Permissions.POLICY_MANAGE)

def test_check_last_admin_success(db):
    user1 = User(provider="github", provider_user_id="1", username="admin1", email="a@example.com")
    user2 = User(provider="github", provider_user_id="2", username="admin2", email="b@example.com")
    db.add_all([user1, user2])
    db.commit()

    team = Team(name="Workspace 1")
    db.add(team)
    db.commit()

    member1 = TeamMember(team_id=team.id, user_id=user1.id, role=Role.ADMIN)
    member2 = TeamMember(team_id=team.id, user_id=user2.id, role=Role.ADMIN)
    db.add_all([member1, member2])
    db.commit()

    # Should not raise because there are 2 admins
    check_last_admin(db, workspace_id=team.id, target_user_id=user1.id)

def test_check_last_admin_failure(db):
    user1 = User(provider="github", provider_user_id="3", username="admin1", email="a@example.com")
    user2 = User(provider="github", provider_user_id="4", username="dev1", email="b@example.com")
    db.add_all([user1, user2])
    db.commit()

    team = Team(name="Workspace 1")
    db.add(team)
    db.commit()

    member1 = TeamMember(team_id=team.id, user_id=user1.id, role=Role.ADMIN)
    member2 = TeamMember(team_id=team.id, user_id=user2.id, role=Role.DEVELOPER)
    db.add_all([member1, member2])
    db.commit()

    # Should raise because user1 is the only admin
    with pytest.raises(HTTPException) as excinfo:
        check_last_admin(db, workspace_id=team.id, target_user_id=user1.id)
    
    assert excinfo.value.status_code == 403
    assert "user is the last ADMIN" in excinfo.value.detail

def test_check_last_admin_non_admin_target(db):
    user1 = User(provider="github", provider_user_id="5", username="dev1", email="a@example.com")
    db.add(user1)
    db.commit()

    team = Team(name="Workspace 1")
    db.add(team)
    db.commit()

    member1 = TeamMember(team_id=team.id, user_id=user1.id, role=Role.DEVELOPER)
    db.add(member1)
    db.commit()

    check_last_admin(db, workspace_id=team.id, target_user_id=user1.id)

def test_can_grant_role():
    from codegate.auth.permissions import can_grant_role
    assert can_grant_role(Role.ADMIN, Role.ADMIN)
    assert can_grant_role(Role.ADMIN, Role.MAINTAINER)
    assert can_grant_role(Role.ADMIN, Role.REVIEWER)
    assert can_grant_role(Role.ADMIN, Role.DEVELOPER)

    assert not can_grant_role(Role.MAINTAINER, Role.ADMIN)
    assert can_grant_role(Role.MAINTAINER, Role.MAINTAINER)
    assert can_grant_role(Role.MAINTAINER, Role.REVIEWER)
    assert can_grant_role(Role.MAINTAINER, Role.DEVELOPER)

    assert not can_grant_role(Role.REVIEWER, Role.ADMIN)
    assert not can_grant_role(Role.REVIEWER, Role.REVIEWER)
    
    assert not can_grant_role(Role.DEVELOPER, Role.DEVELOPER)
