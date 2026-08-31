from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from codegate.database.session import get_db
from codegate.schemas.dashboard import (
    DashboardOverviewResponse,
    PRDashboardItem,
    PullRequestDashboardDetail,
    RepositoryDashboardItem,
    RepositoryDetailResponse,
)
from codegate.services.dashboard_service import dashboard_service

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/overview", response_model=DashboardOverviewResponse)
def get_overview(
    repository_id: Optional[int] = None,
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    db: Session = Depends(get_db)
):
    return dashboard_service.get_overview(db, repository_id, from_date, to_date)

@router.get("/repositories", response_model=List[RepositoryDashboardItem])
def get_repositories(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    sort_by: str = Query("name"),
    sort_order: str = Query("asc"),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    db: Session = Depends(get_db)
):
    allowed_sort_fields = {
        "name", "average_quality", "average_risk", "block_rate", 
        "test_pass_rate", "average_changed_coverage", "last_analysis_at"
    }
    if sort_by not in allowed_sort_fields:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail=f"Invalid sort field: {sort_by}")
        
    return dashboard_service.get_repositories(
        db, page, page_size, search, sort_by, sort_order, from_date, to_date
    )

@router.get("/repositories/{repository_id}", response_model=RepositoryDetailResponse)
def get_repository_detail(
    repository_id: int = Path(...),
    db: Session = Depends(get_db)
):
    from fastapi import HTTPException
    res = dashboard_service.get_repository_detail(db, repository_id)
    if not res:
        raise HTTPException(status_code=404, detail="Repository not found")
    return res

@router.get("/pull-requests", response_model=List[PRDashboardItem])
def get_pull_requests(
    repository_id: Optional[int] = None,
    status: Optional[str] = None,
    policy_decision: Optional[str] = None,
    risk_level: Optional[str] = None,
    quality_grade: Optional[str] = None,
    author: Optional[str] = None,
    search: Optional[str] = None,
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return dashboard_service.get_pull_requests(
        db, repository_id, status, policy_decision, risk_level, quality_grade, author, search, from_date, to_date, page, page_size
    )

@router.get("/pull-requests/{pull_request_id}", response_model=PullRequestDashboardDetail)
def get_pull_request_detail(
    pull_request_id: int = Path(...),
    analysis_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    res = dashboard_service.get_pull_request_detail(db, pull_request_id, analysis_id)
    if not res:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Pull request not found")
    return res
