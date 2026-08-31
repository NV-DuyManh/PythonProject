from typing import Any, List, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from codegate.api.exceptions import ConflictException, NotFoundException
from codegate.database.models import AnalysisRun, PullRequest, Status
from codegate.repositories.analysis_store import analysis_store
from codegate.repositories.pr_store import pr_store
from codegate.schemas.analysis import AnalysisRunCreate


class AnalysisService:
    def create(self, db: Session, pr_id: int, analysis_in: AnalysisRunCreate) -> AnalysisRun:
        pr = pr_store.get_by_id(db, pr_id)
        if not pr:
            raise NotFoundException("Pull request not found")
            
        # AnalysisRunCreate already defaults to status=PENDING
        dump = analysis_in.model_dump()
        dump["pull_request_id"] = pr_id
        return analysis_store.create(db, obj_in=dump)

    def get(self, db: Session, analysis_id: int) -> AnalysisRun:
        analysis = analysis_store.get_by_id(db, analysis_id)
        if not analysis:
            raise NotFoundException("Analysis run not found")
        return analysis

    def list_by_pr(self, db: Session, pr_id: int, skip: int = 0, limit: int = 20) -> Tuple[List[AnalysisRun], int]:
        pr = pr_store.get_by_id(db, pr_id)
        if not pr:
            raise NotFoundException("Pull request not found")
            
        stmt = select(AnalysisRun).where(AnalysisRun.pull_request_id == pr_id)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt)
        
        # Order by created_at desc (newest first)
        stmt = stmt.order_by(AnalysisRun.created_at.desc()).offset(skip).limit(limit)
        items = list(db.scalars(stmt).all())
        
        return items, total

    def list_metrics(self, db: Session, analysis_id: int, skip: int = 0, limit: int = 20, 
                     analyzer: str = None, metric_name: str = None, file_path: str = None) -> Tuple[List[Any], int]:
        from codegate.database.models.analysis import CodeMetric
        analysis = self.get(db, analysis_id)
        if not analysis:
            raise NotFoundException("Analysis run not found")
            
        stmt = select(CodeMetric).where(CodeMetric.analysis_run_id == analysis_id)
        if analyzer:
            stmt = stmt.where(CodeMetric.analyzer == analyzer)
        if metric_name:
            stmt = stmt.where(CodeMetric.metric_name == metric_name)
        if file_path:
            stmt = stmt.where(CodeMetric.file_path == file_path)
            
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt)
        
        stmt = stmt.order_by(CodeMetric.id.asc()).offset(skip).limit(limit)
        items = list(db.scalars(stmt).all())
        
        return items, total

analysis_service = AnalysisService()
