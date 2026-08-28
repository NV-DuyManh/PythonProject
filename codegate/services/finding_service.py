from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from codegate.repositories.finding_store import finding_store
from codegate.repositories.analysis_store import analysis_store
from codegate.database.models import Finding, Severity, Source
from codegate.api.exceptions import NotFoundException

class FindingService:
    def list(self, db: Session, analysis_id: int, severity: Optional[Severity] = None, source: Optional[Source] = None, category: Optional[str] = None, skip: int = 0, limit: int = 20) -> Tuple[List[Finding], int]:
        # Validate analysis exists
        analysis = analysis_store.get_by_id(db, analysis_id)
        if not analysis:
            raise NotFoundException("Analysis run not found")
            
        stmt = select(Finding).where(Finding.analysis_run_id == analysis_id)
        
        if severity:
            stmt = stmt.where(Finding.severity == severity)
        if source:
            stmt = stmt.where(Finding.source == source)
        if category:
            stmt = stmt.where(Finding.category == category)
            
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt)
        
        stmt = stmt.offset(skip).limit(limit)
        items = list(db.scalars(stmt).all())
        
        return items, total

finding_service = FindingService()
