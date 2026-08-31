from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from codegate.database.models import Repository
from codegate.repositories.base_store import BaseStore


class RepositoryStore(BaseStore[Repository]):
    def __init__(self):
        super().__init__(Repository)

    def get_by_full_name(self, db: Session, provider: str, full_name: str) -> Optional[Repository]:
        stmt = select(Repository).where(
            Repository.provider == provider,
            Repository.full_name == full_name
        )
        return db.scalar(stmt)

repo_store = RepositoryStore()
