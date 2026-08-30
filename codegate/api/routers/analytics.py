from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query

from codegate.database.session import get_db
from sqlalchemy.orm import Session

from codegate.schemas.analytics import (
    QualityAnalytics, RiskAnalytics, PolicyAnalytics,
    FindingsAnalytics, TestingAnalytics, ReviewerAnalytics
)
from codegate.services.analytics_service import analytics_service

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

@router.get("/quality", response_model=QualityAnalytics)
def get_quality_analytics(
    repository_id: Optional[int] = None,
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    granularity: str = Query("day"),
    db: Session = Depends(get_db)
):
    return analytics_service.get_quality_analytics(db, repository_id, from_date, to_date)

@router.get("/risk", response_model=RiskAnalytics)
def get_risk_analytics(
    repository_id: Optional[int] = None,
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    db: Session = Depends(get_db)
):
    return analytics_service.get_risk_analytics(db, repository_id, from_date, to_date)

@router.get("/policy", response_model=PolicyAnalytics)
def get_policy_analytics(
    repository_id: Optional[int] = None,
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    db: Session = Depends(get_db)
):
    return analytics_service.get_policy_analytics(db, repository_id, from_date, to_date)

@router.get("/findings", response_model=FindingsAnalytics)
def get_findings_analytics(
    repository_id: Optional[int] = None,
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    changed_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    return analytics_service.get_findings_analytics(db, repository_id, from_date, to_date, changed_only)

@router.get("/testing", response_model=TestingAnalytics)
def get_testing_analytics(
    repository_id: Optional[int] = None,
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    db: Session = Depends(get_db)
):
    return analytics_service.get_testing_analytics(db, repository_id, from_date, to_date)

@router.get("/reviewers", response_model=ReviewerAnalytics)
def get_reviewer_analytics(
    repository_id: Optional[int] = None,
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    db: Session = Depends(get_db)
):
    return analytics_service.get_reviewer_analytics(db, repository_id, from_date, to_date)
