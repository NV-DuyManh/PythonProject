import pytest
from sqlalchemy.exc import IntegrityError
from codegate.database.models import (
    User, Team, TeamMember, Role, Repository, Provider, 
    PullRequest, State, AnalysisRun, Status, Trigger, 
    Finding, Severity, Source
)
from codegate.repositories.repo_store import repo_store
from codegate.repositories.pr_store import pr_store
from codegate.repositories.analysis_store import analysis_store

def test_user_creation(db_session):
    user = User(
        provider="GITHUB", 
        provider_user_id="12345", 
        username="testuser",
        email="test@example.com"
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.created_at is not None

def test_team_and_member(db_session):
    user = User(provider="GITHUB", provider_user_id="123", username="test")
    db_session.add(user)
    
    team = Team(name="Engineering")
    db_session.add(team)
    db_session.commit()
    
    member = TeamMember(team_id=team.id, user_id=user.id, role=Role.DEVELOPER)
    db_session.add(member)
    db_session.commit()
    
    assert len(team.members) == 1
    assert team.members[0].user_id == user.id

def test_repository_unique_constraint(db_session):
    repo1 = Repository(
        provider=Provider.GITHUB,
        owner="org",
        name="repo",
        full_name="org/repo",
        url="https://github.com/org/repo"
    )
    db_session.add(repo1)
    db_session.commit()
    
    repo2 = Repository(
        provider=Provider.GITHUB,
        owner="org2",
        name="repo",
        full_name="org/repo",  # Duplicate full_name and provider
        url="https://github.com/org2/repo"
    )
    db_session.add(repo2)
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_pull_request_and_analysis(db_session):
    # Setup Repo
    repo = repo_store.create(db_session, obj_in={
        "provider": Provider.GITHUB,
        "owner": "org",
        "name": "repo",
        "full_name": "org/repo",
        "url": "https://github.com/org/repo"
    })
    
    # Create PR
    pr = pr_store.create(db_session, obj_in={
        "repository_id": repo.id,
        "number": 1,
        "title": "Fix bug",
        "author_username": "dev1",
        "source_branch": "feature-a",
        "target_branch": "main",
        "state": State.OPEN,
        "head_sha": "abc1234"
    })
    
    assert pr.id is not None
    
    # Create Analysis Runs
    run1 = analysis_store.create(db_session, obj_in={
        "pull_request_id": pr.id,
        "head_sha": "abc1234",
        "status": Status.COMPLETED,
        "trigger": Trigger.WEBHOOK
    })
    
    run2 = analysis_store.create(db_session, obj_in={
        "pull_request_id": pr.id,
        "head_sha": "def5678", # New commit
        "status": Status.PENDING,
        "trigger": Trigger.PUSH
    })
    
    runs = analysis_store.list_by_pull_request(db_session, pr.id)
    assert len(runs) == 2
    
    latest = analysis_store.get_latest_for_pull_request(db_session, pr.id)
    assert latest.id == run2.id

def test_finding_persistence(db_session):
    repo = repo_store.create(db_session, obj_in={
        "provider": Provider.GITHUB,
        "owner": "org",
        "name": "repo",
        "full_name": "org/repo",
        "url": "https://github.com/org/repo"
    })
    pr = pr_store.create(db_session, obj_in={
        "repository_id": repo.id,
        "number": 1,
        "title": "Fix bug",
        "author_username": "dev1",
        "source_branch": "feature-a",
        "target_branch": "main",
        "state": State.OPEN,
        "head_sha": "abc1234"
    })
    run = analysis_store.create(db_session, obj_in={
        "pull_request_id": pr.id,
        "head_sha": "abc1234",
        "status": Status.COMPLETED,
        "trigger": Trigger.WEBHOOK
    })
    
    finding = Finding(
        analysis_run_id=run.id,
        source=Source.AI,
        category="Security",
        severity=Severity.HIGH,
        title="Hardcoded Secret",
        description="Found a secret in code",
        raw_data={"secret_type": "AWS_KEY"}
    )
    db_session.add(finding)
    db_session.commit()
    
    assert finding.id is not None
    assert finding.raw_data["secret_type"] == "AWS_KEY"
