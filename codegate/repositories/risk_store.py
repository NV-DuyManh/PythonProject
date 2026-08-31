from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from codegate.database.models import RiskScore
from codegate.repositories.base_store import BaseStore


class RiskScoreStore(BaseStore[RiskScore]):
    def __init__(self):
        super().__init__(RiskScore)

    def get_latest_for_analysis(self, db: Session, analysis_run_id: int) -> Optional[RiskScore]:
        stmt = select(RiskScore).where(
            RiskScore.analysis_run_id == analysis_run_id
        ).order_by(desc(RiskScore.created_at), desc(RiskScore.id)).limit(1)
        return db.scalar(stmt)

    def upsert(self, db: Session, obj_in: dict) -> RiskScore:
        """Upsert a RiskScore based on (analysis_run_id, calculation_version)"""
        analysis_run_id = obj_in['analysis_run_id']
        calculation_version = obj_in['calculation_version']
        
        stmt = select(RiskScore).where(
            RiskScore.analysis_run_id == analysis_run_id,
            RiskScore.calculation_version == calculation_version
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
            new_obj = RiskScore(**obj_in)
            db.add(new_obj)
            db.commit()
            db.refresh(new_obj)
            return new_obj

risk_store = RiskScoreStore()
