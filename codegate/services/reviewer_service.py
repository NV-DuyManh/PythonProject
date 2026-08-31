import json
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from codegate.database.models import AnalysisRun, PullRequest, PullRequestFile, Repository, TeamMember, User
from codegate.engines.reviewer.config import ReviewerEngineConfig
from codegate.engines.reviewer.engine import ReviewerRecommendationEngine
from codegate.engines.reviewer.schemas import ReviewerRecommendationResult
from codegate.repositories.analysis_store import analysis_store
from codegate.repositories.repo_store import repo_store
from codegate.repositories.reviewer_store import reviewer_config_store, reviewer_recommendation_store


class ReviewerRecommendationService:
    def get_config(self, db: Session, repository_id: int) -> dict:
        config = reviewer_config_store.get_by_repository(db, repository_id)
        if not config:
            config = reviewer_config_store.create_default(db, repository_id)
        return self._config_to_dict(config)

    def update_config(self, db: Session, repository_id: int, updates: dict[str, Any]) -> dict:
        config = reviewer_config_store.update_config(db, repository_id, updates)
        return self._config_to_dict(config)

    def _config_to_dict(self, config) -> dict:
        return {
            "enabled": config.enabled,
            "top_n": config.top_n,
            "minimum_recommendation_score": config.minimum_recommendation_score,
            "history_days": config.history_days,
            "max_history_commits": config.max_history_commits,
            "allow_external_codeowners": config.allow_external_codeowners,
            "eligible_roles": json.loads(config.eligible_roles_json),
            "revision": config.revision
        }

    def _get_eligible_user_ids(self, db: Session, roles: List[str]) -> List[int]:
        """
        Global team members filter. We assume members of any team with matching role are eligible.
        (For a more complex setup, we would filter by repository's team).
        """
        from sqlalchemy import select
        stmt = select(TeamMember.user_id).where(TeamMember.role.in_(roles))
        user_ids = list(db.scalars(stmt).all())
        return list(set(user_ids))

    def evaluate_and_persist(self, db: Session, analysis_run: AnalysisRun, repo_path: str) -> Optional[dict]:
        repo_id = analysis_run.pull_request.repository_id
        db_config = reviewer_config_store.get_by_repository(db, repo_id)
        if not db_config:
            db_config = reviewer_config_store.create_default(db, repo_id)
            
        config = ReviewerEngineConfig(
            enabled=db_config.enabled,
            top_n=db_config.top_n,
            minimum_recommendation_score=db_config.minimum_recommendation_score,
            history_days=db_config.history_days,
            max_history_commits=db_config.max_history_commits,
            allow_external_codeowners=db_config.allow_external_codeowners,
            eligible_roles=json.loads(db_config.eligible_roles_json)
        )
        
        pr = analysis_run.pull_request
        changed_files = [f.file_path for f in pr.files]
        
        # Author exclusion
        author_username = pr.author_username
        
        eligible_user_ids = self._get_eligible_user_ids(db, config.eligible_roles)
        
        # Engine execution
        try:
            # Using base_sha
            base_sha = pr.base_sha
            
            result = ReviewerRecommendationEngine.evaluate(
                db=db,
                config=config,
                repo_root=repo_path,
                changed_files=changed_files,
                base_sha=base_sha,
                eligible_user_ids=eligible_user_ids,
                author_provider_username=author_username
            )
        except Exception as e:
            result = ReviewerRecommendationResult(
                status="FAILED",
                engine_version="reviewer-v1",
                error_message=str(e)
            )
            
        # Persist
        recommendation_data = {
            "status": result.status,
            "eligible_candidate_count": result.eligible_candidate_count,
            "recommended_candidate_count": result.recommended_candidate_count,
            "is_complete": result.is_complete,
            "available_weight": result.available_weight,
            "missing_sources_json": json.dumps(result.missing_sources),
            "unresolved_codeowners_json": json.dumps(result.unresolved_codeowners),
            "config_snapshot_json": json.dumps(self._config_to_dict(db_config)),
            "error_message": result.error_message
        }
        
        candidates_data = []
        for i, c in enumerate(result.recommendations):
            candidates_data.append(c.to_db_dict(rank=i+1))
            
        rec = reviewer_recommendation_store.persist_recommendation(
            db=db,
            analysis_run_id=analysis_run.id,
            config_id=db_config.id,
            config_revision=db_config.revision,
            engine_version=result.engine_version,
            recommendation_data=recommendation_data,
            candidates_data=candidates_data
        )
        
        return self._format_response(rec)

    def get_latest(self, db: Session, analysis_run_id: int) -> Optional[dict]:
        rec = reviewer_recommendation_store.get_by_analysis(db, analysis_run_id)
        if not rec:
            return None
        return self._format_response(rec)

    def _format_response(self, rec) -> dict:
        candidates = []
        for c in rec.candidates:
            candidates.append({
                "user_id": c.user_id,
                "provider_username": c.provider_username,
                "rank": c.rank,
                "overall_score": c.overall_score,
                "codeowners_score": c.codeowners_score,
                "exact_file_score": c.exact_file_score,
                "directory_score": c.directory_score,
                "recency_score": c.recency_score,
                "exact_file_commits": c.exact_file_commits,
                "directory_commits": c.directory_commits,
                "file_coverage_percent": c.file_coverage_percent,
                "matched_files": json.loads(c.matched_files_json or "[]"),
                "reasons": json.loads(c.reasons_json or "[]")
            })
            
        # Ensure ranked order
        candidates = sorted(candidates, key=lambda x: x["rank"])
        
        return {
            "status": rec.status,
            "engine_version": rec.engine_version,
            "config_revision": rec.config_revision,
            "is_complete": rec.is_complete,
            "eligible_candidate_count": rec.eligible_candidate_count,
            "recommended_candidate_count": rec.recommended_candidate_count,
            "missing_sources": json.loads(rec.missing_sources_json or "[]"),
            "unresolved_codeowners": json.loads(rec.unresolved_codeowners_json or "[]"),
            "recommendations": candidates,
            "error_message": rec.error_message
        }

reviewer_service = ReviewerRecommendationService()
