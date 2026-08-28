from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from codegate.api.dependencies import get_db
from codegate.api.pagination import get_pagination_params, PaginationParams, paginate
from codegate.schemas.pagination import PaginatedResponse
from codegate.schemas.repository import RepositoryCreate, RepositoryUpdate, RepositoryResponse
from codegate.services.repository_service import repository_service
from codegate.database.models import Provider

router = APIRouter(prefix="/repositories", tags=["Repositories"])

@router.post("", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
def create_repository(
    repo_in: RepositoryCreate,
    db: Session = Depends(get_db)
):
    return repository_service.create(db, repo_in)

@router.get("", response_model=PaginatedResponse[RepositoryResponse])
def list_repositories(
    provider: Optional[Provider] = None,
    active: Optional[bool] = None,
    search: Optional[str] = None,
    pagination: PaginationParams = Depends(get_pagination_params),
    db: Session = Depends(get_db)
):
    skip = (pagination.page - 1) * pagination.page_size
    items, total = repository_service.list(
        db, provider=provider, active=active, search=search, skip=skip, limit=pagination.page_size
    )
    return paginate(items, total, pagination)

@router.get("/{repo_id}", response_model=RepositoryResponse)
def get_repository(
    repo_id: int,
    db: Session = Depends(get_db)
):
    return repository_service.get(db, repo_id)

@router.patch("/{repo_id}", response_model=RepositoryResponse)
def update_repository(
    repo_id: int,
    repo_in: RepositoryUpdate,
    db: Session = Depends(get_db)
):
    return repository_service.update(db, repo_id, repo_in)

@router.delete("/{repo_id}", response_model=RepositoryResponse)
def delete_repository(
    repo_id: int,
    db: Session = Depends(get_db)
):
    return repository_service.delete(db, repo_id)
