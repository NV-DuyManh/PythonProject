import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from codegate.database.models import Base, Team, Repository

@pytest.fixture
def postgres_session():
    db_url = os.environ.get("POSTGRES_TEST_URL")
    if not db_url:
        pytest.skip("POSTGRES_TEST_URL not set")
        
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_postgres_tenant_isolation(postgres_session):
    # Setup
    workspace_a = Team(id=1, name="Workspace A")
    workspace_b = Team(id=2, name="Workspace B")
    postgres_session.add_all([workspace_a, workspace_b])
    postgres_session.commit()
    
    repo_a = Repository(id=1, name="repo_a", owner="org", full_name="org/repo_a", provider="github", url="https://github.com/org/repo_a", workspace_id=1)
    postgres_session.add(repo_a)
    postgres_session.commit()
    
    # Query logic simulating the endpoints
    repos_b = postgres_session.query(Repository).filter(Repository.workspace_id == 2).all()
    assert len(repos_b) == 0
    
    repos_a = postgres_session.query(Repository).filter(Repository.workspace_id == 1).all()
    assert len(repos_a) == 1
    assert repos_a[0].name == "repo_a"

def test_postgres_fk_cascade_restrict(postgres_session):
    # Attempt to delete workspace A, should fail because RESTRICT is in place
    import sqlalchemy.exc
    
    workspace_a = Team(id=1, name="Workspace A")
    postgres_session.add(workspace_a)
    postgres_session.commit()
    
    repo_a = Repository(id=1, name="repo_a", owner="org", full_name="org/repo_a", provider="github", url="https://github.com/org/repo_a", workspace_id=1)
    postgres_session.add(repo_a)
    postgres_session.commit()
    
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        postgres_session.delete(workspace_a)
        postgres_session.commit()
    
    postgres_session.rollback()
