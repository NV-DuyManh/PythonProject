from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from codegate.api.dependencies import get_db
from codegate.api.pagination import get_pagination_params, PaginationParams, paginate
from codegate.schemas.pagination import PaginatedResponse
from codegate.schemas.analysis import AnalysisRunCreate, AnalysisRunResponse, CodeMetricResponse
from codegate.schemas.quality import QualityScoreResponse
from codegate.schemas.risk import RiskScoreResponse
from codegate.schemas.policy import PolicyEvaluationResponse
from codegate.services.analysis_service import analysis_service
from codegate.services.quality_service import quality_service
from codegate.services.risk_service import risk_service
from codegate.services.policy_service import quality_policy_service
from codegate.repositories.policy_store import policy_evaluation_store

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

@router.get("/analyses/{analysis_id}/metrics", response_model=PaginatedResponse[CodeMetricResponse])
def list_analysis_metrics(
    analysis_id: int,
    analyzer: Optional[str] = Query(None, description="Filter by analyzer name"),
    metric_name: Optional[str] = Query(None, description="Filter by metric name"),
    file_path: Optional[str] = Query(None, description="Filter by file path"),
    pagination: PaginationParams = Depends(get_pagination_params),
    db: Session = Depends(get_db)
):
    skip = (pagination.page - 1) * pagination.page_size
    items, total = analysis_service.list_metrics(
        db, analysis_id=analysis_id, skip=skip, limit=pagination.page_size,
        analyzer=analyzer, metric_name=metric_name, file_path=file_path
    )
    return paginate(items, total, pagination)

@router.get("/analyses/{analysis_id}/quality", response_model=QualityScoreResponse)
def get_analysis_quality(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve the latest quality score for an analysis run"""
    return quality_service.get_quality(db, analysis_id)

@router.post("/analyses/{analysis_id}/quality/recalculate", response_model=QualityScoreResponse)
def recalculate_analysis_quality(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Recalculate the quality score for an analysis run"""
    return quality_service.recalculate(db, analysis_id)

@router.get("/analyses/{analysis_id}/risk", response_model=RiskScoreResponse)
def get_analysis_risk(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve the latest risk score for an analysis run"""
    return risk_service.get_risk(db, analysis_id)

@router.post("/analyses/{analysis_id}/risk/recalculate", response_model=RiskScoreResponse)
def recalculate_analysis_risk(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Recalculate the risk score for an analysis run"""
    return risk_service.recalculate(db, analysis_id)

@router.get("/analyses/{analysis_id}/policy", response_model=PolicyEvaluationResponse)
def get_analysis_policy(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve the latest policy evaluation for an analysis run"""
    evaluation = policy_evaluation_store.get_latest_for_analysis(db, analysis_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Policy evaluation not found")
    return evaluation

@router.post("/analyses/{analysis_id}/policy/evaluate", response_model=PolicyEvaluationResponse)
def evaluate_analysis_policy(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Recalculate policy evaluation for an analysis run"""
    analysis = analysis_service.get(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    # Using None publisher here for manual recalculation so we don't spam checks,
    # or we can pass a dummy publisher. The prompt requires evaluating using current policy.
    # The default is publisher=None
    return quality_policy_service.evaluate_and_publish(db, analysis)
