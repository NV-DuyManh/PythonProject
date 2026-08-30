import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from codegate.database.base import Base
from codegate.database.models import Repository, AnalysisRun
from codegate.repositories.policy_store import quality_policy_store, policy_evaluation_store

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_default_policy(db_session):
    repo = Repository(provider="GITHUB", owner="test", name="repo", full_name="test/repo", url="http")
    db_session.add(repo)
    db_session.commit()
    
    policy = quality_policy_store.create_default(db_session, repo.id)
    assert policy is not None
    assert policy.quality_pass_threshold == 80.0
    assert policy.revision == 1

def test_update_policy_increments_revision(db_session):
    repo = Repository(provider="GITHUB", owner="test", name="repo", full_name="test/repo", url="http")
    db_session.add(repo)
    db_session.commit()
    
    policy = quality_policy_store.create_default(db_session, repo.id)
    
    updated = quality_policy_store.update_policy(db_session, repo.id, {"quality_block_threshold": 50.0})
    assert updated.quality_block_threshold == 50.0
    assert updated.revision == 2

def test_policy_evaluation_upsert(db_session):
    repo = Repository(provider="GITHUB", owner="test", name="repo", full_name="test/repo", url="http")
    db_session.add(repo)
    db_session.commit()
    
    from codegate.database.models import PullRequest
    pr = PullRequest(repository_id=repo.id, number=1, head_sha="abc", title="test", author_username="test", source_branch="src", target_branch="main", state="OPEN")
    db_session.add(pr)
    db_session.commit()
    
    run = AnalysisRun(pull_request_id=pr.id, head_sha="abc", status="PENDING", trigger="MANUAL")
    db_session.add(run)
    db_session.commit()
    
    policy = quality_policy_store.create_default(db_session, repo.id)
    
    eval_data = {
        "analysis_run_id": run.id,
        "policy_id": policy.id,
        "policy_engine_version": "v1",
        "policy_revision": policy.revision,
        "decision": "PASS",
        "config_snapshot_json": {"test": "val"},
        "evaluation_status": "COMPLETED"
    }
    
    ev1 = policy_evaluation_store.upsert(db_session, eval_data)
    assert ev1.id is not None
    
    # upsert same
    eval_data["decision"] = "WARNING"
    ev2 = policy_evaluation_store.upsert(db_session, eval_data)
    
    assert ev1.id == ev2.id
    assert ev2.decision == "WARNING"
    
    # different revision -> creates new
    eval_data["policy_revision"] = 2
    ev3 = policy_evaluation_store.upsert(db_session, eval_data)
    
    assert ev3.id != ev1.id
