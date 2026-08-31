import os
import sys
from datetime import datetime, timezone

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from codegate.database.models import AnalysisRun, PolicyEvaluation, PullRequest, QualityScore, Repository, RiskScore
from codegate.database.models.pull_request import State
from codegate.database.session import SessionLocal


def run_crud_test():
    print("Starting CRUD test...")
    db = SessionLocal()
    
    try:
        # 1. CREATE
        # Repository
        import time
        unique_id = int(time.time())
        repo = Repository(
            provider="GITHUB",
            owner="test-org",
            name=f"test-crud-repo-{unique_id}",
            full_name=f"test-org/test-crud-repo-{unique_id}",
            url=f"https://github.com/test-org/test-crud-repo-{unique_id}",
            active=True,
            data_source="LIVE"
        )
        db.add(repo)
        db.commit()
        db.refresh(repo)
        repo_id = repo.id
        print(f"Created Repository ID: {repo_id}")

        # PullRequest
        pr = PullRequest(
            repository_id=repo_id,
            provider_pr_id="12345",
            number=42,
            title="Test CRUD PR",
            description="Testing DB operations",
            author_username="crud-user",
            source_branch="feat/test",
            target_branch="main",
            state=State.OPEN,
            head_sha="abcdef123456",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(pr)
        db.commit()
        db.refresh(pr)
        pr_id = pr.id
        print(f"Created PullRequest ID: {pr_id}")

        # AnalysisRun
        run = AnalysisRun(
            pull_request_id=pr_id,
            head_sha="abcdef123456",
            status="COMPLETED",
            trigger="webhook",
            ai_model="test-model"
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        run_id = run.id
        print(f"Created AnalysisRun ID: {run_id}")

        # QualityScore
        qs = QualityScore(
            analysis_run_id=run_id,
            overall_score=95.0,
            grade="A",
            available_weight=1.0,
            breakdown_json={"code_style": 100, "bug_risk": 90},
            calculation_version="1.0.0"
        )
        db.add(qs)
        
        # RiskScore
        rs = RiskScore(
            analysis_run_id=run_id,
            overall_risk=0.05,
            risk_level="LOW",
            available_weight=1.0,
            breakdown_json={"security": 0, "complexity": 10},
            calculation_version="1.0.0"
        )
        db.add(rs)

        # QualityPolicy
        from codegate.database.models import QualityPolicy
        qp = QualityPolicy(
            repository_id=repo_id,
            name="default-quality-policy",
            policy_engine_version="1.0",
            revision=1
        )
        db.add(qp)
        db.commit()
        db.refresh(qp)
        qp_id = qp.id

        # PolicyEvaluation
        pe = PolicyEvaluation(
            analysis_run_id=run_id,
            policy_id=qp_id,
            policy_engine_version="1.0",
            policy_revision=1,
            evaluation_status="COMPLETED",
            decision="PASS",
            passed_rules_count=5,
            warning_rules_count=0,
            blocked_rules_count=0
        )
        db.add(pe)

        db.commit()
        print("Created QualityScore, RiskScore, PolicyEvaluation.")

        # 2. READ & VERIFY
        read_repo = db.query(Repository).filter(Repository.id == repo_id).first()
        assert read_repo.full_name == f"test-org/test-crud-repo-{unique_id}", "Repo name mismatch"
        
        read_qs = db.query(QualityScore).filter(QualityScore.analysis_run_id == run_id).first()
        assert read_qs.overall_score == 95.0, "QualityScore mismatch"
        print("READ assertions passed.")

        # 3. UPDATE
        read_repo.active = False
        db.commit()
        db.refresh(read_repo)
        assert read_repo.active is False, "Update failed"
        print("UPDATE assertion passed.")

        # 4. DELETE (Clean up)
        db.delete(read_repo)  # Cascades should drop PR, Run, Scores, PolicyEvals
        db.commit()
        
        verify_deleted = db.query(Repository).filter(Repository.id == repo_id).first()
        assert verify_deleted is None, "Delete failed"
        verify_pr_deleted = db.query(PullRequest).filter(PullRequest.id == pr_id).first()
        assert verify_pr_deleted is None, "Cascade delete of PR failed"
        
        print("DELETE and Cascade assertions passed.")
        print("ALL CRUD TESTS PASSED SUCCESSFULLY!")

    except Exception as e:
        db.rollback()
        print(f"CRUD TEST FAILED: {str(e)}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    run_crud_test()
