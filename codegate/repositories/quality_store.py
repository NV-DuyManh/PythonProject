from typing import Optional, List, Any
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert

from codegate.database.models import QualityScore
from codegate.repositories.base_store import BaseStore

class QualityScoreStore(BaseStore[QualityScore]):
    def __init__(self):
        super().__init__(QualityScore)

    def get_latest_for_analysis(self, db: Session, analysis_run_id: int) -> Optional[QualityScore]:
        stmt = select(QualityScore).where(
            QualityScore.analysis_run_id == analysis_run_id
        ).order_by(desc(QualityScore.created_at), desc(QualityScore.id)).limit(1)
        return db.scalar(stmt)

    def upsert(self, db: Session, obj_in: dict) -> QualityScore:
        """Upsert a QualityScore based on (analysis_run_id, calculation_version)"""
        # SQLite upsert
        stmt = insert(QualityScore).values(**obj_in)
        
        # update on conflict
        update_dict = {
            c.name: c
            for c in stmt.excluded
            if c.name not in ('id', 'analysis_run_id', 'calculation_version', 'created_at')
        }
        
        stmt = stmt.on_conflict_do_update(
            index_elements=['analysis_run_id', 'calculation_version'],
            set_=update_dict
        )
        
        db.execute(stmt)
        db.commit()
        
        # return the updated/inserted object
        select_stmt = select(QualityScore).where(
            QualityScore.analysis_run_id == obj_in['analysis_run_id'],
            QualityScore.calculation_version == obj_in['calculation_version']
        )
        return db.scalar(select_stmt)

quality_store = QualityScoreStore()
