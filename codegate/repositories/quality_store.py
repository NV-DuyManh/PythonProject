from typing import Any, List, Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

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
        analysis_run_id = obj_in['analysis_run_id']
        calculation_version = obj_in['calculation_version']
        
        stmt = select(QualityScore).where(
            QualityScore.analysis_run_id == analysis_run_id,
            QualityScore.calculation_version == calculation_version
        )
        existing = db.scalar(stmt)
        
        if existing:
            update_dict = {
                k: v for k, v in obj_in.items()
                if k not in ('id', 'analysis_run_id', 'calculation_version', 'created_at')
            }
            if update_dict:
                for k, v in update_dict.items():
                    setattr(existing, k, v)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            new_obj = QualityScore(**obj_in)
            db.add(new_obj)
            db.commit()
            db.refresh(new_obj)
            return new_obj

quality_store = QualityScoreStore()
