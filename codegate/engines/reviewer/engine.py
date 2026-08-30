from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
import os

from sqlalchemy.orm import Session

from codegate.engines.reviewer.config import ReviewerEngineConfig
from codegate.engines.reviewer.schemas import (
    ReviewerIdentityInfo, 
    RecommendationCandidate, 
    ReviewerRecommendationResult
)
from codegate.engines.reviewer import REVIEWER_ENGINE_VERSION
from codegate.engines.reviewer.identity import IdentityResolver
from codegate.engines.reviewer.codeowners import CodeownersParser
from codegate.engines.reviewer.git_history import GitHistoryAnalyzer
from codegate.engines.reviewer.scoring import ReviewerScoringModel
from codegate.engines.reviewer.explanation import ReviewerExplanationGenerator

class ReviewerRecommendationEngine:
    @staticmethod
    def evaluate(
        db: Session,
        config: ReviewerEngineConfig,
        repo_root: str,
        changed_files: List[str],
        base_sha: str,
        eligible_user_ids: List[int],
        author_provider_username: Optional[str] = None,
        now: Optional[datetime] = None
    ) -> ReviewerRecommendationResult:
        if now is None:
            now = datetime.now(timezone.utc)
            
        result = ReviewerRecommendationResult(
            status="PARTIAL",
            engine_version=REVIEWER_ENGINE_VERSION,
        )
        
        if not config.enabled:
            result.status = "SKIPPED"
            return result
            
        # 1. Identity Resolution
        identities = IdentityResolver.resolve_candidates(
            db, eligible_user_ids, author_provider_username
        )
        
        if not identities:
            result.status = "NO_ELIGIBLE_REVIEWERS"
            return result
            
        # Initialize candidates
        candidates_map: Dict[int, RecommendationCandidate] = {}
        for ident in identities:
            if ident.is_author:
                continue # Exclude author
            candidates_map[ident.user_id] = RecommendationCandidate(
                user_id=ident.user_id,
                provider_username=ident.provider_username
            )
            
        if not candidates_map:
            result.status = "NO_ELIGIBLE_REVIEWERS"
            return result
            
        result.eligible_candidate_count = len(candidates_map)
        
        # 2. CODEOWNERS Analysis
        has_codeowners = False
        unresolved_owners = set()
        codeowners_path = CodeownersParser.get_codeowners_path(repo_root)
        
        if codeowners_path:
            rules = CodeownersParser.parse_file(codeowners_path)
            if rules:
                has_codeowners = True
                for file_path in changed_files:
                    owners = CodeownersParser.find_owners(file_path, rules)
                    for owner in owners:
                        # Find candidate
                        candidate_ident = IdentityResolver.map_provider_username_to_candidate(owner, identities)
                        if candidate_ident:
                            if candidate_ident.is_author:
                                continue
                            c = candidates_map.get(candidate_ident.user_id)
                            if c:
                                if file_path not in c.matched_files:
                                    c.matched_files.append(file_path)
                                if "codeowner_matched_files" not in c.evidence:
                                    c.evidence["codeowner_matched_files"] = []
                                if file_path not in c.evidence["codeowner_matched_files"]:
                                    c.evidence["codeowner_matched_files"].append(file_path)
                        else:
                            unresolved_owners.add(owner)
                            if config.allow_external_codeowners:
                                # Not implemented: we do not add unknown users as candidates
                                pass
        
        if not has_codeowners:
            result.missing_sources.append("CODEOWNERS")
            
        result.unresolved_codeowners = list(unresolved_owners)
        
        # 3. Git History Analysis
        has_history = False
        if base_sha:
            try:
                history_map = GitHistoryAnalyzer.analyze_history(
                    repo_root=repo_root,
                    base_sha=base_sha,
                    changed_files=changed_files,
                    history_days=config.history_days,
                    max_commits=config.max_history_commits,
                    now=now
                )
                if history_map:
                    has_history = True
                    for email, hist_data in history_map.items():
                        candidate_ident = IdentityResolver.map_git_email_to_candidate(email, identities)
                        if candidate_ident:
                            if candidate_ident.is_author:
                                continue
                            c = candidates_map.get(candidate_ident.user_id)
                            if c:
                                c.exact_file_commits += hist_data["exact_commits"]
                                c.directory_commits += hist_data["dir_commits"]
                                last_activity = hist_data["last_activity"]
                                
                                if last_activity:
                                    # Calculate days ago
                                    # Normalize to UTC
                                    if last_activity.tzinfo is None:
                                        last_activity = last_activity.replace(tzinfo=timezone.utc)
                                    days_ago = (now - last_activity).days
                                    if days_ago < 0:
                                        days_ago = 0
                                        
                                    existing_days = c.evidence.get("last_activity_days_ago")
                                    if existing_days is None or days_ago < existing_days:
                                        c.evidence["last_activity_days_ago"] = days_ago
            except Exception as e:
                # History failed, treat as missing source
                result.error_message = f"Git history analysis failed: {str(e)}"
                
        if not has_history:
            result.missing_sources.append("GIT_HISTORY")
            
        if not has_codeowners and not has_history:
            result.status = "NO_SUITABLE_REVIEWER"
            result.is_complete = False
            return result
            
        if not result.missing_sources:
            result.status = "COMPLETED"
        else:
            result.status = "PARTIAL"
            result.is_complete = False
            
        # 4. Scoring
        candidates_list = list(candidates_map.values())
        
        scored_candidates, available_weight = ReviewerScoringModel.score_candidates(
            candidates=candidates_list,
            total_changed_files=len(changed_files),
            has_codeowners=has_codeowners,
            has_history=has_history,
            now=now
        )
        
        result.available_weight = available_weight
        
        # Filter by minimum score
        eligible_candidates = [
            c for c in scored_candidates 
            if c.overall_score >= config.minimum_recommendation_score
        ]
        
        if not eligible_candidates:
            result.status = "NO_SUITABLE_REVIEWER"
            return result
            
        # 5. Ranking
        ranked_candidates = ReviewerScoringModel.rank_candidates(eligible_candidates)
        
        # 6. Top N
        top_candidates = ranked_candidates[:config.top_n]
        
        # 7. Explanation
        for c in top_candidates:
            c.reasons = ReviewerExplanationGenerator.generate_reasons(c)
            
        result.recommendations = top_candidates
        result.recommended_candidate_count = len(top_candidates)
        
        return result
