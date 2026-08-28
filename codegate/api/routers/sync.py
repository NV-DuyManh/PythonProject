from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

from codegate.api.dependencies import get_db
from codegate.services.github_sync_service import GithubSyncService
from codegate.schemas.pull_request import PullRequestResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])

class SyncRequest(BaseModel):
    pr_url: str

@router.post("/github/pull-request", response_model=PullRequestResponse)
async def sync_github_pull_request(request: SyncRequest, db: Session = Depends(get_db)):
    """
    Manually triggers a synchronization of a GitHub PR into the CodeGate database.
    """
    try:
        sync_service = GithubSyncService(db)
        repo, pr = sync_service.sync_pull_request(request.pr_url)
        return pr
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Failed to sync pull request")
        raise HTTPException(status_code=500, detail="Internal server error")
