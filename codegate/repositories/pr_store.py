from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from codegate.database.models import PullRequest
from codegate.repositories.base_store import BaseStore

class PullRequestStore(BaseStore[PullRequest]):
    def __init__(self):
        super().__init__(PullRequest)

    def get_by_repo_and_number(self, db: Session, repository_id: int, number: int) -> Optional[PullRequest]:
        stmt = select(PullRequest).where(
            PullRequest.repository_id == repository_id,
            PullRequest.number == number
        )
        return db.scalar(stmt)

    def list_by_repository(self, db: Session, repository_id: int, skip: int = 0, limit: int = 100) -> List[PullRequest]:
        stmt = select(PullRequest).where(
            PullRequest.repository_id == repository_id
        ).offset(skip).limit(limit)
        return list(db.scalars(stmt).all())

pr_store = PullRequestStore()
