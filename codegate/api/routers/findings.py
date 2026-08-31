from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from codegate.api.dependencies import get_db
from codegate.api.pagination import PaginationParams, get_pagination_params, paginate
from codegate.database.models import Severity, Source
from codegate.schemas.finding import FindingResponse
from codegate.schemas.pagination import PaginatedResponse
from codegate.services.finding_service import finding_service

router = APIRouter(tags=["Findings"])

@router.get("/analyses/{analysis_id}/findings", response_model=PaginatedResponse[FindingResponse])
def list_findings_for_analysis(
    analysis_id: int,
    severity: Optional[Severity] = None,
    source: Optional[Source] = None,
    category: Optional[str] = None,
    pagination: PaginationParams = Depends(get_pagination_params),
    db: Session = Depends(get_db)
):
    skip = (pagination.page - 1) * pagination.page_size
    items, total = finding_service.list(
        db, 
        analysis_id=analysis_id, 
        severity=severity, 
        source=source, 
        category=category, 
        skip=skip, 
        limit=pagination.page_size
    )
    return paginate(items, total, pagination)
