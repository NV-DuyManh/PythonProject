from typing import Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session

from pr_agent.git_providers import get_git_provider_with_context
from codegate.database.models.pull_request import PullRequest
from codegate.database.models.repository import Repository
from codegate.services.repository_service import RepositoryService
from codegate.services.pr_service import PullRequestService

class GithubSyncService:
    """
    Synchronizes a GitHub PR (via PR-Agent's GithubProvider) into the CodeGate database.
    """
    def __init__(self, db: Session):
        self.db = db
        self.repo_service = RepositoryService()
        self.pr_service = PullRequestService()

    def sync_pull_request(self, pr_url: str) -> Tuple[Repository, PullRequest]:
        """
        Uses PR-Agent's provider to fetch the PR, then upserts the Repository and PullRequest
        into the CodeGate DB.
        """
        # Note: If no token is configured, this will throw an exception.
        # But this is exactly what we want (it requires the system to be configured correctly).
        provider = get_git_provider_with_context(pr_url)
        
        if not getattr(provider, "pr", None):
            raise ValueError(f"Provider failed to load a PR object for {pr_url}")
            
        pr_obj = provider.pr
        repo_obj = getattr(provider, "repo", None)

        if not repo_obj and hasattr(pr_obj, "base") and hasattr(pr_obj.base, "repo"):
            repo_obj = pr_obj.base.repo

        # Extract Repository Data
        # If repo_obj doesn't have full_name, extract from URL
        repo_full_name = getattr(repo_obj, "full_name", "")
        if not repo_full_name:
            # pr_url e.g. https://github.com/owner/repo/pull/1
            parts = pr_url.rstrip("/").split("/")
            if len(parts) >= 6:
                repo_full_name = f"{parts[-4]}/{parts[-3]}"
        if not repo_full_name:
            repo_full_name = pr_url.split("github.com/")[-1].split("/pull")[0]

        repo_url = f"https://github.com/{repo_full_name}"
        
        # 1. Upsert Repository
        from codegate.repositories.repo_store import repo_store
        # We need to find it by full_name
        repository = repo_store.get_by_full_name(self.db, "GITHUB", repo_full_name)
        if not repository:
            # We bypass the pydantic schema for internal sync since we have direct models
            owner_name = repo_full_name.split("/")[0] if "/" in repo_full_name else ""
            repo_name = repo_full_name.split("/")[-1]
            repository = Repository(
                name=repo_name,
                owner=owner_name,
                full_name=repo_full_name,
                provider="GITHUB",
                url=repo_url,
                active=True,
                data_source="LIVE"
            )
            self.db.add(repository)
            self.db.commit()
            self.db.refresh(repository)

        # Extract PR Data
        pr_number = getattr(provider, "pr_num", None)
        if not pr_number and hasattr(pr_obj, "number"):
            pr_number = pr_obj.number
        
        title = provider.get_title()
        description = getattr(pr_obj, "body", "") or ""
        author = getattr(pr_obj.user, "login", "") if hasattr(pr_obj, "user") else ""
        
        target_branch = provider.get_pr_branch()
        # Head branch is sometimes tricky, let's grab it from the provider if possible
        source_branch = getattr(pr_obj.head, "ref", "") if hasattr(pr_obj, "head") else ""
        head_sha = getattr(pr_obj.head, "sha", "") if hasattr(pr_obj, "head") else ""
        
        state = getattr(pr_obj, "state", "OPEN").upper()
        if getattr(pr_obj, "merged", False):
            state = "MERGED"

        changed_files_list = provider.get_diff_files() or []
        changed_files_count = len(changed_files_list)

        # 2. Upsert PullRequest
        # Check if PR exists
        pull_request = self.db.query(PullRequest).filter(
            PullRequest.repository_id == repository.id,
            PullRequest.number == pr_number
        ).first()

        if pull_request:
            # Update
            pull_request.title = title
            pull_request.description = description
            pull_request.state = state
            pull_request.head_sha = head_sha
            pull_request.changed_files = changed_files_count
            self.db.commit()
            self.db.refresh(pull_request)
        else:
            # Create
            pull_request = PullRequest(
                repository_id=repository.id,
                number=pr_number,
                title=title,
                description=description,
                author_username=author,
                source_branch=source_branch,
                target_branch=target_branch,
                state=state,
                changed_files=changed_files_count,
                head_sha=head_sha,
                provider_created_at=getattr(pr_obj, "created_at", None),
                provider_updated_at=getattr(pr_obj, "updated_at", None),
            )
            self.db.add(pull_request)
            self.db.commit()
            self.db.refresh(pull_request)

        return repository, pull_request