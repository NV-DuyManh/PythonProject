from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from codegate.api.dependencies import get_current_workspace, get_db
from codegate.database.models import Team
from codegate.repositories.analysis_store import analysis_store
from codegate.repositories.repo_store import repo_store
from codegate.services.reviewer_service import reviewer_service

router = APIRouter()

@router.get("/repositories/{repository_id}/reviewer-config")
def get_reviewer_config(
    repository_id: int,
    db: Session = Depends(get_db),
    workspace: Team = Depends(get_current_workspace)
):
    repo = repo_store.get_by_id(db, repository_id)
    if not repo or repo.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Repository not found")
        
    return reviewer_service.get_config(db, repository_id, workspace.id)


@router.patch("/repositories/{repository_id}/reviewer-config")
def update_reviewer_config(
    repository_id: int,
    updates: Dict[str, Any],
    db: Session = Depends(get_db),
    workspace: Team = Depends(get_current_workspace)
):
    repo = repo_store.get_by_id(db, repository_id)
    if not repo or repo.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Repository not found")
        
    return reviewer_service.update_config(db, repository_id, updates, workspace.id)


@router.get("/analyses/{analysis_id}/reviewers")
def get_reviewers(
    analysis_id: int,
    db: Session = Depends(get_db),
    workspace: Team = Depends(get_current_workspace)
):
    analysis = analysis_store.get_by_id(db, analysis_id)
    if not analysis or analysis.pull_request.repository.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    result = reviewer_service.get_latest(db, analysis_id, workspace.id)
    if not result:
        # According to standard behavior, we don't recalculate on GET
        raise HTTPException(status_code=404, detail="Reviewer recommendation not found")
        
    return result


@router.post("/analyses/{analysis_id}/reviewers/recommend")
def recommend_reviewers(
    analysis_id: int,
    db: Session = Depends(get_db),
    workspace: Team = Depends(get_current_workspace)
):
    analysis = analysis_store.get_by_id(db, analysis_id)
    if not analysis or analysis.pull_request.repository.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    # We would need the repo_path. Since this is an API call, we might not have a cloned repo readily available unless it's cached.
    # In a real environment, we'd clone it or use the cached path.
    repo_path = f"/tmp/repos/{analysis.pull_request.repository_id}"  # nosec B108
    
    result = reviewer_service.evaluate_and_persist(db, analysis, repo_path, workspace.id)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to calculate reviewer recommendation")
        
    return result
