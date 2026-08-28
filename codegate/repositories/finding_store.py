from typing import List, Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from codegate.database.models import Finding
from codegate.repositories.base_store import BaseStore

class FindingStore(BaseStore[Finding]):
    def __init__(self):
        super().__init__(Finding)

    def list_by_analysis(self, db: Session, analysis_run_id: int, skip: int = 0, limit: int = 100) -> List[Finding]:
        stmt = select(Finding).where(
            Finding.analysis_run_id == analysis_run_id
        ).offset(skip).limit(limit)
        return list(db.scalars(stmt).all())

    def bulk_create(self, db: Session, findings: List[dict[str, Any]]) -> List[Finding]:
        db_objs = [self.model(**f) for f in findings]
        db.add_all(db_objs)
        db.commit()
        for obj in db_objs:
            db.refresh(obj)
        return db_objs

finding_store = FindingStore()
