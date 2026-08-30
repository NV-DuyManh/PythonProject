from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from codegate.engines.reviewer.schemas import RecommendationCandidate

class ReviewerScoringModel:
    CODEOWNERS_WEIGHT = 40.0
    EXACT_FILE_WEIGHT = 30.0
    DIRECTORY_WEIGHT = 20.0
    RECENCY_WEIGHT = 10.0

    @staticmethod
    def calculate_recency_score(days_ago: Optional[int]) -> Optional[float]:
        if days_ago is None:
            return None
            
        if days_ago <= 30:
            return 100.0
        elif days_ago <= 90:
            return 80.0
        elif days_ago <= 180:
            return 50.0
        elif days_ago <= 365:
            return 20.0
        else:
            return 0.0

    @staticmethod
    def score_candidates(
        candidates: List[RecommendationCandidate],
        total_changed_files: int,
        has_codeowners: bool,
        has_history: bool,
        now: datetime
    ) -> Tuple[List[RecommendationCandidate], float]:
        """
        Scores all candidates and returns the normalized list along with the available weight.
        """
        available_weight = 0.0
        
        if has_codeowners:
            available_weight += ReviewerScoringModel.CODEOWNERS_WEIGHT
            
        if has_history:
            available_weight += ReviewerScoringModel.EXACT_FILE_WEIGHT
            available_weight += ReviewerScoringModel.DIRECTORY_WEIGHT
            available_weight += ReviewerScoringModel.RECENCY_WEIGHT
            
        if available_weight == 0:
            return candidates, 0.0
            
        # Find max history commits for normalization
        max_exact = 0
        max_dir = 0
        
        if has_history:
            for c in candidates:
                if c.exact_file_commits > max_exact:
                    max_exact = c.exact_file_commits
                if c.directory_commits > max_dir:
                    max_dir = c.directory_commits
                    
        for c in candidates:
            total_score = 0.0
            
            # CODEOWNERS
            if has_codeowners:
                if total_changed_files > 0:
                    matched_count = len(c.matched_files)
                    c.codeowners_score = min(100.0, (matched_count / total_changed_files) * 100.0)
                    c.file_coverage_percent = c.codeowners_score
                else:
                    c.codeowners_score = 0.0
                    c.file_coverage_percent = 0.0
                total_score += c.codeowners_score * (ReviewerScoringModel.CODEOWNERS_WEIGHT / available_weight)
            else:
                c.codeowners_score = None
                
            # History
            if has_history:
                # Exact
                if max_exact > 0:
                    c.exact_file_score = (c.exact_file_commits / max_exact) * 100.0
                else:
                    c.exact_file_score = 0.0
                total_score += c.exact_file_score * (ReviewerScoringModel.EXACT_FILE_WEIGHT / available_weight)
                
                # Directory
                if max_dir > 0:
                    c.directory_score = (c.directory_commits / max_dir) * 100.0
                else:
                    c.directory_score = 0.0
                total_score += c.directory_score * (ReviewerScoringModel.DIRECTORY_WEIGHT / available_weight)
                
                # Recency
                days_ago = c.evidence.get("last_activity_days_ago")
                if days_ago is not None:
                    c.recency_score = ReviewerScoringModel.calculate_recency_score(days_ago)
                else:
                    c.recency_score = 0.0
                
                total_score += c.recency_score * (ReviewerScoringModel.RECENCY_WEIGHT / available_weight)
            else:
                c.exact_file_score = None
                c.directory_score = None
                c.recency_score = None
                
            c.overall_score = round(total_score, 2)
            
        return candidates, available_weight

    @staticmethod
    def rank_candidates(candidates: List[RecommendationCandidate]) -> List[RecommendationCandidate]:
        """
        Sort candidates using deterministic tie-breaking:
        1. overall_score DESC
        2. CODEOWNERS score DESC
        3. exact_file_commits DESC
        4. directory_commits DESC
        5. provider_username ASC case-insensitive
        """
        def sort_key(c: RecommendationCandidate):
            return (
                -c.overall_score,
                -(c.codeowners_score or 0.0),
                -c.exact_file_commits,
                -c.directory_commits,
                c.provider_username.lower()
            )
            
        return sorted(candidates, key=sort_key)
