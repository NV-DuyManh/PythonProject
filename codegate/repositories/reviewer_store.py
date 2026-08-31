import json
from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from codegate.database.models import (
    ReviewerRecommendation,
    ReviewerRecommendationCandidate,
    ReviewerRecommendationConfig,
)
from codegate.repositories.base_store import BaseStore


class ReviewerRecommendationConfigStore(BaseStore[ReviewerRecommendationConfig]):
    def __init__(self):
        super().__init__(ReviewerRecommendationConfig)

    def get_by_repository(self, db: Session, repository_id: int) -> Optional[ReviewerRecommendationConfig]:
        stmt = select(self.model).where(self.model.repository_id == repository_id)
        return db.scalars(stmt).first()

    def create_default(self, db: Session, repository_id: int) -> ReviewerRecommendationConfig:
        config = self.model(
            repository_id=repository_id,
            enabled=True,
            top_n=3,
            minimum_recommendation_score=20.0,
            history_days=365,
            max_history_commits=2000,
            allow_external_codeowners=False,
            eligible_roles_json=json.dumps(["ADMIN", "MAINTAINER", "REVIEWER"]),
            revision=1
        )
        db.add(config)
        db.commit()
        db.refresh(config)
        return config

    def update_config(self, db: Session, repository_id: int, updates: dict[str, Any]) -> ReviewerRecommendationConfig:
        config = self.get_by_repository(db, repository_id)
        if not config:
            config = self.create_default(db, repository_id)
            
        # Increment revision
        config.revision += 1
        
        for k, v in updates.items():
            setattr(config, k, v)
            
        db.add(config)
        db.commit()
        db.refresh(config)
        return config


class ReviewerRecommendationStore(BaseStore[ReviewerRecommendation]):
    def __init__(self):
        super().__init__(ReviewerRecommendation)

    def get_by_analysis(self, db: Session, analysis_run_id: int) -> Optional[ReviewerRecommendation]:
        stmt = select(self.model).where(
            self.model.analysis_run_id == analysis_run_id
        ).order_by(self.model.id.desc())
        return db.scalars(stmt).first()
        
    def persist_recommendation(
        self, 
        db: Session, 
        analysis_run_id: int, 
        config_id: int, 
        config_revision: int, 
        engine_version: str,
        recommendation_data: dict[str, Any],
        candidates_data: List[dict[str, Any]]
    ) -> ReviewerRecommendation:
        # Check if one already exists for this exact logical identity
        stmt = select(self.model).where(
            self.model.analysis_run_id == analysis_run_id,
            self.model.config_id == config_id,
            self.model.config_revision == config_revision,
            self.model.engine_version == engine_version
        )
        existing = db.scalars(stmt).first()
        
        if existing:
            # Update existing recommendation
            for k, v in recommendation_data.items():
                setattr(existing, k, v)
            # Remove old candidates
            for candidate in list(existing.candidates):
                db.delete(candidate)
            existing.candidates = []
            
            # Add new candidates
            for c_data in candidates_data:
                candidate = ReviewerRecommendationCandidate(**c_data)
                existing.candidates.append(candidate)
                
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new recommendation
            rec = self.model(
                analysis_run_id=analysis_run_id,
                config_id=config_id,
                config_revision=config_revision,
                engine_version=engine_version,
                **recommendation_data
            )
            for c_data in candidates_data:
                candidate = ReviewerRecommendationCandidate(**c_data)
                rec.candidates.append(candidate)
                
            db.add(rec)
            db.commit()
            db.refresh(rec)
            return rec

reviewer_config_store = ReviewerRecommendationConfigStore()
reviewer_recommendation_store = ReviewerRecommendationStore()
