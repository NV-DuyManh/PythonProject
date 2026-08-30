from typing import List
from codegate.engines.reviewer.schemas import RecommendationCandidate

class ReviewerExplanationGenerator:
    @staticmethod
    def generate_reasons(candidate: RecommendationCandidate) -> List[str]:
        reasons = []
        
        # CODEOWNERS reason
        codeowner_matches = candidate.evidence.get("codeowner_matched_files", [])
        if codeowner_matches:
            if len(codeowner_matches) == 1:
                reasons.append("CODEOWNER for 1 changed file.")
            else:
                reasons.append(f"CODEOWNER for {len(codeowner_matches)} changed files.")
                
        # Exact File reason
        if candidate.exact_file_commits > 0:
            if candidate.exact_file_commits == 1:
                reasons.append("1 historical commit to files changed by this PR.")
            else:
                reasons.append(f"{candidate.exact_file_commits} historical commits to files changed by this PR.")
                
        # Directory reason
        if candidate.directory_commits > 0:
            reasons.append(f"Strong directory expertise ({candidate.directory_commits} commits in relevant directories).")
            
        # Recency reason
        days_ago = candidate.evidence.get("last_activity_days_ago")
        if days_ago is not None:
            if days_ago <= 30:
                reasons.append("Relevant activity within the last 30 days.")
            elif days_ago <= 90:
                reasons.append("Relevant activity within the last 90 days.")
            elif days_ago <= 180:
                reasons.append("Relevant activity within the last 6 months.")
            elif days_ago <= 365:
                reasons.append("Relevant activity within the last year.")
                
        # Deduplicate while preserving order
        seen = set()
        final_reasons = []
        for r in reasons:
            if r not in seen:
                final_reasons.append(r)
                seen.add(r)
                
        return final_reasons
