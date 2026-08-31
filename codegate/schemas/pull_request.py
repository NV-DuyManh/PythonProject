from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from codegate.database.models import State
from codegate.schemas.analysis import AnalysisRunResponse
from codegate.schemas.repository import RepositoryResponse


class PullRequestBase(BaseModel):
    number: int
    title: str
    description: Optional[str] = None
    author_username: str
    source_branch: str
    target_branch: str
    state: State = State.OPEN
    head_sha: Optional[str] = None
    base_sha: Optional[str] = None
    additions: Optional[int] = 0
    deletions: Optional[int] = 0
    changed_files: Optional[int] = 0

class PullRequestCreate(PullRequestBase):
    pass

class PullRequestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    state: Optional[State] = None
    head_sha: Optional[str] = None
    base_sha: Optional[str] = None
    additions: Optional[int] = None
    deletions: Optional[int] = None
    changed_files: Optional[int] = None

class PullRequestResponse(PullRequestBase):
    id: int
    repository_id: int
    created_at: datetime
    updated_at: datetime

    # Extra fields for management API
    analysis_count: Optional[int] = 0
    latest_analysis: Optional[AnalysisRunResponse] = None

    @field_validator("additions", "deletions", "changed_files", mode="before")
    @classmethod
    def coerce_none_to_zero(cls, v: object) -> int:
        return v if v is not None else 0

    model_config = ConfigDict(from_attributes=True)

