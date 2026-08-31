from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from codegate.database.models.policy import PolicyEvaluation, QualityPolicy
from codegate.repositories.base_store import BaseStore


class QualityPolicyStore(BaseStore[QualityPolicy]):
    def __init__(self):
        super().__init__(QualityPolicy)

    def get_by_repository(self, db: Session, repository_id: int) -> Optional[QualityPolicy]:
        stmt = select(QualityPolicy).where(
            QualityPolicy.repository_id == repository_id,
            QualityPolicy.active == True
        )
        return db.scalar(stmt)

    def create_default(self, db: Session, repository_id: int) -> QualityPolicy:
        existing = self.get_by_repository(db, repository_id)
        if existing:
            return existing
            
        policy = QualityPolicy(
            repository_id=repository_id,
            name="Default Quality Policy",
            policy_engine_version="policy-v1",
            revision=1
        )
        db.add(policy)
        db.commit()
        db.refresh(policy)
        return policy

    def update_policy(self, db: Session, repository_id: int, obj_in: dict) -> QualityPolicy:
        existing = self.get_by_repository(db, repository_id)
        if not existing:
            # If no policy exists, create the default one first
            existing = self.create_default(db, repository_id)
            
        # We need to increment the revision and create a new record or update the existing one?
        # The prompt says: "Khi config repository policy thay đổi: revision += 1"
        # Since we use `policy_id` in evaluation and want to keep history?
        # Actually, "Không hard-delete policy history nếu không cần."
        # If we update the row, the old evaluations will point to this policy_id, but the `policy_revision` and `config_snapshot_json` in PolicyEvaluation will preserve the history.
        # Let's just update the row and increment revision, as PolicyEvaluation captures the snapshot.
        
        # update fields
        for k, v in obj_in.items():
            if hasattr(existing, k) and k not in ('id', 'repository_id', 'revision', 'created_at'):
                setattr(existing, k, v)
        
        existing.revision += 1
        db.commit()
        db.refresh(existing)
        return existing


class PolicyEvaluationStore(BaseStore[PolicyEvaluation]):
    def __init__(self):
        super().__init__(PolicyEvaluation)

    def get_latest_for_analysis(self, db: Session, analysis_run_id: int) -> Optional[PolicyEvaluation]:
        stmt = select(PolicyEvaluation).where(
            PolicyEvaluation.analysis_run_id == analysis_run_id
        ).order_by(desc(PolicyEvaluation.created_at), desc(PolicyEvaluation.id)).limit(1)
        return db.scalar(stmt)

    def upsert(self, db: Session, obj_in: dict) -> PolicyEvaluation:
        """Cross-dialect upsert for PolicyEvaluation based on (analysis_run_id, policy_id, policy_revision)"""
        analysis_run_id = obj_in['analysis_run_id']
        policy_id = obj_in['policy_id']
        policy_revision = obj_in['policy_revision']
        
        stmt = select(PolicyEvaluation).where(
            PolicyEvaluation.analysis_run_id == analysis_run_id,
            PolicyEvaluation.policy_id == policy_id,
            PolicyEvaluation.policy_revision == policy_revision
        )
        existing = db.scalar(stmt)
        
        if existing:
            update_dict = {
                k: v for k, v in obj_in.items()
                if k not in ('id', 'analysis_run_id', 'policy_id', 'policy_revision', 'created_at')
            }
            if update_dict:
                for k, v in update_dict.items():
                    setattr(existing, k, v)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            new_obj = PolicyEvaluation(**obj_in)
            db.add(new_obj)
            db.commit()
            db.refresh(new_obj)
            return new_obj


quality_policy_store = QualityPolicyStore()
policy_evaluation_store = PolicyEvaluationStore()
