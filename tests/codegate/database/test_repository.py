import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select
from codegate.database.models import Repository, Provider, GitHubConnection

def test_repository_unique_identity(db_session: Session):
    """
    Verify that alice/backend and bob/backend are distinguishable
    and duplicate owner/name for the same provider fails.
    """
    repo_alice = Repository(
        provider=Provider.GITHUB,
        owner="alice",
        name="backend",
        full_name="alice/backend",
        url="https://github.com/alice/backend",
        workspace_id=1
    )
    repo_bob = Repository(
        provider=Provider.GITHUB,
        owner="bob",
        name="backend",
        full_name="bob/backend",
        url="https://github.com/bob/backend",
        workspace_id=1
    )
    
    db_session.add_all([repo_alice, repo_bob])
    db_session.commit()
    
    assert repo_alice.id is not None
    assert repo_bob.id is not None
    assert repo_alice.id != repo_bob.id
    
    # Try duplicate connection_id and provider_repository_id
    repo_dup = Repository(
        provider=Provider.GITHUB,
        owner="alice",
        name="backend",
        full_name="alice/backend_2",
        url="https://github.com/alice/backend_2",
        workspace_id=1,
        github_connection_id=1,
        provider_repository_id="12345"
    )
    repo_alice.github_connection_id = 1
    repo_alice.provider_repository_id = "12345"
    db_session.add(repo_dup)

    with pytest.raises(IntegrityError):
        db_session.commit()
        
    db_session.rollback()


def test_repository_connection_scoping(db_session: Session):
    """
    Verify repositories can be mapped to separate connections securely.
    """
    conn_a = GitHubConnection(account_login="account_a")
    conn_b = GitHubConnection(account_login="account_b")
    db_session.add_all([conn_a, conn_b])
    db_session.commit()
    
    repo_a1 = Repository(
        provider=Provider.GITHUB, owner="account_a", name="repo1",
        full_name="account_a/repo1", url="https://github.com/account_a/repo1",
        github_connection_id=conn_a.id
    )
    repo_a2 = Repository(
        provider=Provider.GITHUB, owner="account_a", name="repo2",
        full_name="account_a/repo2", url="https://github.com/account_a/repo2",
        github_connection_id=conn_a.id
    )
    repo_b1 = Repository(
        provider=Provider.GITHUB, owner="account_b", name="repo1",
        full_name="account_b/repo1", url="https://github.com/account_b/repo1",
        github_connection_id=conn_b.id
    )
    
    db_session.add_all([repo_a1, repo_a2, repo_b1])
    db_session.commit()
    
    repos_for_a = db_session.execute(select(Repository).where(Repository.github_connection_id == conn_a.id)).scalars().all()
    repos_for_b = db_session.execute(select(Repository).where(Repository.github_connection_id == conn_b.id)).scalars().all()
    
    assert len(repos_for_a) == 2
    assert len(repos_for_b) == 1
    assert repo_a1 in repos_for_a
    assert repo_b1 in repos_for_b
