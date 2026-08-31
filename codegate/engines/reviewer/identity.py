from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from codegate.database.models import User
from codegate.engines.reviewer.schemas import ReviewerIdentityInfo


class IdentityResolver:
    @staticmethod
    def resolve_candidates(db: Session, user_ids: List[int], author_provider_username: Optional[str] = None) -> List[ReviewerIdentityInfo]:
        """
        Load ReviewerIdentityInfo for eligible user_ids.
        Excludes the PR author using exact provider_username matching.
        No fuzzy matching is allowed.
        """
        if not user_ids:
            return []
            
        stmt = select(User).where(User.id.in_(user_ids))
        users = list(db.scalars(stmt).all())
        
        identities = []
        for user in users:
            username = user.username
            if username and (username.lower().endswith("[bot]") or username.lower() == "dependabot"):
                continue # Exclude bots
                
            is_author = False
            if author_provider_username and username.lower() == author_provider_username.lower():
                is_author = True
                
            identities.append(
                ReviewerIdentityInfo(
                    user_id=user.id,
                    provider_username=user.username,
                    email=user.email,
                    is_author=is_author
                )
            )
            
        return identities

    @staticmethod
    def map_git_email_to_candidate(git_email: str, candidates: List[ReviewerIdentityInfo]) -> Optional[ReviewerIdentityInfo]:
        """
        Deterministically map a git email to an eligible candidate.
        Matches exactly by email. No fuzzy logic.
        """
        git_email = git_email.lower().strip()
        for candidate in candidates:
            if candidate.email and candidate.email.lower().strip() == git_email:
                return candidate
        return None

    @staticmethod
    def map_provider_username_to_candidate(username: str, candidates: List[ReviewerIdentityInfo]) -> Optional[ReviewerIdentityInfo]:
        """
        Deterministically map a GitHub/CODEOWNERS handle to a candidate.
        Matches exactly (case-insensitive).
        """
        # Remove leading '@' if present
        if username.startswith("@"):
            username = username[1:]
            
        username = username.lower().strip()
        for candidate in candidates:
            if candidate.provider_username.lower().strip() == username:
                return candidate
        return None
