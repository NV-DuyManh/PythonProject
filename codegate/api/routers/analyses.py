from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from codegate.api.dependencies import get_db
from codegate.api.pagination import get_pagination_params, PaginationParams, paginate
from codegate.schemas.pagination import PaginatedResponse
from codegate.schemas.analysis import AnalysisRunCreate, AnalysisRunResponse
from codegate.services.analysis_service import analysis_service

router = APIRouter(tags=["Analyses"])

@router.post("/pull-requests/{pr_id}/analyses", response_model=AnalysisRunResponse, status_code=status.HTTP_201_CREATED)
def create_manual_analysis(
    pr_id: int,
    analysis_in: AnalysisRunCreate,
    db: Session = Depends(get_db)
):
    return analysis_service.create(db, pr_id, analysis_in)

@router.get("/pull-requests/{pr_id}/analyses", response_model=PaginatedResponse[AnalysisRunResponse])
def list_analyses_for_pr(
    pr_id: int,
    pagination: PaginationParams = Depends(get_pagination_params),
    db: Session = Depends(get_db)
):
    skip = (pagination.page - 1) * pagination.page_size
    items, total = analysis_service.list_by_pr(
        db, pr_id=pr_id, skip=skip, limit=pagination.page_size
    )
    return paginate(items, total, pagination)

@router.get("/analyses/{analysis_id}", response_model=AnalysisRunResponse)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    return analysis_service.get(db, analysis_id)
