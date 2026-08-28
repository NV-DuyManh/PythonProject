import pytest
from sqlalchemy.exc import IntegrityError
from codegate.database.models import User, Team, TeamMember, Role, Provider, State
from codegate.repositories.repo_store import repo_store
from codegate.repositories.pr_store import pr_store

def test_pull_request_unique_constraint(db_session):
    repo = repo_store.create(db_session, obj_in={
        "provider": Provider.GITHUB,
        "owner": "org",
        "name": "repo2",
        "full_name": "org/repo2",
        "url": "https://github.com/org/repo2"
    })
    
    pr_store.create(db_session, obj_in={
        "repository_id": repo.id,
        "number": 100,
        "title": "Fix bug",
        "author_username": "dev1",
        "source_branch": "feature-a",
        "target_branch": "main",
        "state": State.OPEN,
        "head_sha": "abc1234"
    })
    
    # Attempt to create duplicate PR with same number in same repo
    with pytest.raises(IntegrityError):
        pr_store.create(db_session, obj_in={
            "repository_id": repo.id,
            "number": 100,
            "title": "Another bug",
            "author_username": "dev2",
            "source_branch": "feature-b",
            "target_branch": "main",
            "state": State.OPEN,
            "head_sha": "def5678"
        })

def test_team_member_unique_constraint(db_session):
    user = User(provider="GITHUB", provider_user_id="999", username="test999")
    db_session.add(user)
    
    team = Team(name="Design")
    db_session.add(team)
    db_session.commit()
    
    member1 = TeamMember(team_id=team.id, user_id=user.id, role=Role.DEVELOPER)
    db_session.add(member1)
    db_session.commit()
    
    # Attempt to add same user to same team again
    member2 = TeamMember(team_id=team.id, user_id=user.id, role=Role.ADMIN)
    db_session.add(member2)
    with pytest.raises(IntegrityError):
        db_session.commit()
