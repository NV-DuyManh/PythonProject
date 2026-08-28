from sqlalchemy.orm import Session
from codegate.repositories.repo_store import repo_store
from codegate.repositories.pr_store import pr_store
from codegate.database.models import Provider, State

class PullRequestService:
    def create_or_update_pr(
        self,
        db: Session,
        provider: Provider,
        repo_owner: str,
        repo_name: str,
        repo_url: str,
        pr_number: int,
        pr_title: str,
        author: str,
        source_branch: str,
        target_branch: str,
        state: State,
        head_sha: str
    ):
        full_name = f"{repo_owner}/{repo_name}"
        repo = repo_store.get_by_full_name(db, provider, full_name)
        if not repo:
            repo = repo_store.create(db, obj_in={
                "provider": provider,
                "owner": repo_owner,
                "name": repo_name,
                "full_name": full_name,
                "url": repo_url
            })
        
        pr = pr_store.get_by_repo_and_number(db, repo.id, pr_number)
        if pr:
            # Update existing
            pr = pr_store.update(db, db_obj=pr, obj_in={
                "title": pr_title,
                "state": state,
                "head_sha": head_sha
            })
        else:
            # Create new
            pr = pr_store.create(db, obj_in={
                "repository_id": repo.id,
                "number": pr_number,
                "title": pr_title,
                "author_username": author,
                "source_branch": source_branch,
                "target_branch": target_branch,
                "state": state,
                "head_sha": head_sha
            })
            
        return pr

pr_service = PullRequestService()
