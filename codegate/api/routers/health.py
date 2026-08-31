from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from codegate.api.dependencies import get_db

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Check API and Database health"""
    try:
        # Check database connectivity
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
        
    return {
        "status": "ok",
        "database": db_status
    }

@router.get("/info")
def get_info():
    """Get API information"""
    return {
        "name": "CodeGate API",
        "version": "0.1.0"
    }
