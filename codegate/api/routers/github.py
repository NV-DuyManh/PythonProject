from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from codegate.database.session import get_db
from codegate.database.models.github import GitHubConnection
from pydantic import BaseModel
from typing import Dict, Any, List

router = APIRouter(prefix="/integrations/github", tags=["GitHub Integration"])

@router.get("/connections")
def get_github_connections(db: Session = Depends(get_db)):
    connections = db.scalars(select(GitHubConnection)).all()
    return [{"id": c.id, "account_login": c.account_login, "status": c.status, "auth_type": c.auth_type} for c in connections]

@router.post("/connections/{connection_id}/disconnect")
def disconnect_github(connection_id: int, db: Session = Depends(get_db)):
    conn = db.get(GitHubConnection, connection_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    conn.status = "disconnected"
    db.commit()
    return {"status": "success", "message": "Connection disconnected successfully"}

@router.get("/connections/{connection_id}/repositories")
def get_available_repositories(connection_id: int, db: Session = Depends(get_db)):
    conn = db.get(GitHubConnection, connection_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    # Mocking available repositories for the demo flow
    return [
        {"id": 101, "name": "backend", "full_name": f"{conn.account_login}/backend", "private": True},
        {"id": 102, "name": "frontend", "full_name": f"{conn.account_login}/frontend", "private": False}
    ]

class ImportRepositoryRequest(BaseModel):
    full_name: str
    
@router.post("/connections/{connection_id}/import")
def import_repository(connection_id: int, request: ImportRepositoryRequest, db: Session = Depends(get_db)):
    conn = db.get(GitHubConnection, connection_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    return {"status": "success", "message": f"Repository {request.full_name} imported"}
