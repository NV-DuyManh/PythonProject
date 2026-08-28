from typing import Optional, List, Any
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from codegate.database.models import AnalysisRun
from codegate.repositories.base_store import BaseStore

class AnalysisStore(BaseStore[AnalysisRun]):
    def __init__(self):
        super().__init__(AnalysisRun)

    def list_by_pull_request(self, db: Session, pull_request_id: int, skip: int = 0, limit: int = 100) -> List[AnalysisRun]:
        stmt = select(AnalysisRun).where(
            AnalysisRun.pull_request_id == pull_request_id
        ).order_by(desc(AnalysisRun.created_at)).offset(skip).limit(limit)
        return list(db.scalars(stmt).all())

    def get_latest_for_pull_request(self, db: Session, pull_request_id: int) -> Optional[AnalysisRun]:
        stmt = select(AnalysisRun).where(
            AnalysisRun.pull_request_id == pull_request_id
        ).order_by(desc(AnalysisRun.created_at)).limit(1)
        return db.scalar(stmt)

    def update_status(self, db: Session, run_id: int, status: str, **kwargs: Any) -> Optional[AnalysisRun]:
        run = self.get_by_id(db, run_id)
        if run:
            run.status = status
            for k, v in kwargs.items():
                setattr(run, k, v)
            db.commit()
            db.refresh(run)
        return run

analysis_store = AnalysisStore()
