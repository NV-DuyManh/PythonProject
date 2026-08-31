from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from codegate.api.dependencies import get_db
from codegate.api.pagination import PaginationParams, get_pagination_params, paginate
from codegate.database.models import State
from codegate.schemas.pagination import PaginatedResponse
from codegate.schemas.pull_request import PullRequestCreate, PullRequestResponse, PullRequestUpdate
from codegate.services.pr_service import pr_service

router = APIRouter(tags=["Pull Requests"])

@router.post("/repositories/{repository_id}/pull-requests", response_model=PullRequestResponse, status_code=status.HTTP_201_CREATED)
def create_pull_request(
    repository_id: int,
    pr_in: PullRequestCreate,
    db: Session = Depends(get_db)
):
    return pr_service.create(db, repository_id, pr_in)

@router.get("/repositories/{repository_id}/pull-requests", response_model=PaginatedResponse[PullRequestResponse])
def list_pull_requests_by_repo(
    repository_id: int,
    state: Optional[State] = None,
    author: Optional[str] = None,
    search: Optional[str] = None,
    pagination: PaginationParams = Depends(get_pagination_params),
    db: Session = Depends(get_db)
):
    skip = (pagination.page - 1) * pagination.page_size
    items, total = pr_service.list(
        db, repository_id=repository_id, state=state, author=author, search=search, skip=skip, limit=pagination.page_size
    )
    return paginate(items, total, pagination)

@router.get("/pull-requests", response_model=PaginatedResponse[PullRequestResponse])
def list_pull_requests(
    state: Optional[State] = None,
    author: Optional[str] = None,
    search: Optional[str] = None,
    pagination: PaginationParams = Depends(get_pagination_params),
    db: Session = Depends(get_db)
):
    skip = (pagination.page - 1) * pagination.page_size
    items, total = pr_service.list(
        db, state=state, author=author, search=search, skip=skip, limit=pagination.page_size
    )
    return paginate(items, total, pagination)

@router.get("/pull-requests/{pr_id}", response_model=PullRequestResponse)
def get_pull_request(
    pr_id: int,
    db: Session = Depends(get_db)
):
    return pr_service.get(db, pr_id)

@router.patch("/pull-requests/{pr_id}", response_model=PullRequestResponse)
def update_pull_request(
    pr_id: int,
    pr_in: PullRequestUpdate,
    db: Session = Depends(get_db)
):
    return pr_service.update(db, pr_id, pr_in)
