import hashlib
import hmac
import logging
import json
from fastapi import APIRouter, Request, Response, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from pr_agent.config_loader import get_settings
from codegate.api.dependencies import get_db
from codegate.database.models.webhook import WebhookEvent
from codegate.database.models.analysis import Trigger
from codegate.services.github_sync_service import GithubSyncService
from codegate.services.analysis_orchestrator import AnalysisOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/github_webhooks", tags=["webhooks"])

def verify_signature(body: bytes, secret: str, signature: str):
    if not signature:
        raise HTTPException(status_code=401, detail="Missing X-Hub-Signature-256 header")
    
    hash_object = hmac.new(secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

from codegate.database.session import SessionLocal

async def process_webhook_task(delivery_id: str, event_type: str, action: str, body: dict):
    """
    Background task to process the webhook event.
    """
    with SessionLocal() as db:
        webhook_event = db.query(WebhookEvent).filter_by(provider="github", delivery_id=delivery_id).first()
        if not webhook_event:
            return
            
        try:
            if event_type == "pull_request":
                if action in ["opened", "synchronize", "reopened", "closed"]:
                    # The PR URL is usually present in the payload
                    pr_url = body.get("pull_request", {}).get("html_url")
                    if not pr_url:
                        raise ValueError("No PR URL found in payload")
                    # Extract installation_id for PR-Agent authentication
                    installation_id = body.get("installation", {}).get("id")
                    if installation_id:
                        from pr_agent.config_loader import get_settings
                        get_settings().set("GITHUB.INSTALLATION_ID", installation_id)
                    
                    # 1. Sync Data
                    sync_service = GithubSyncService(db)
                    repo, pr = sync_service.sync_pull_request(pr_url)
                    
                    # 2. Trigger Analysis if needed
                    if action in ["opened", "synchronize"]:
                        orchestrator = AnalysisOrchestrator(db)
                        await orchestrator.trigger_analysis(pr, pr_url, force=False, trigger_type=Trigger.WEBHOOK)
            
            # Mark processed
            webhook_event.status = "PROCESSED"
            db.commit()
        except Exception as e:
            logger.exception("Failed to process webhook event")
            webhook_event.status = "FAILED"
            webhook_event.error_message = str(e)
            db.commit()

@router.post("")
async def handle_github_webhooks(
    request: Request, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    body_bytes = await request.body()
    try:
        body = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error parsing JSON")

    # Verify signature
    webhook_secret = getattr(get_settings().github, 'webhook_secret', None)
    if webhook_secret:
        signature_header = request.headers.get('x-hub-signature-256', None)
        verify_signature(body_bytes, webhook_secret, signature_header)

    event_type = request.headers.get("X-GitHub-Event", "unknown")
    delivery_id = request.headers.get("X-GitHub-Delivery", "")
    
    if not delivery_id:
        return {"status": "ignored", "reason": "No delivery id"}

    # Deduplication
    existing = db.query(WebhookEvent).filter_by(provider="github", delivery_id=delivery_id).first()
    if existing:
        return {"status": "ignored", "reason": "Duplicate event"}

    action = body.get("action", "unknown")
    repo_full_name = body.get("repository", {}).get("full_name")
    pr_number = body.get("pull_request", {}).get("number")
    payload_hash = hashlib.sha256(body_bytes).hexdigest()

    webhook_event = WebhookEvent(
        provider="github",
        delivery_id=delivery_id,
        event_type=event_type,
        action=action,
        repository_full_name=repo_full_name,
        pull_request_number=pr_number,
        payload_hash=payload_hash,
        status="PENDING"
    )
    db.add(webhook_event)
    db.commit()

    # Pass db instance could be problematic across threads depending on engine,
    # but since this is SQLite or Postgres standard session, we might need a fresh session.
    # In FastAPI TestClient this is fine for static pool.
    # For actual production, a worker queue like Celery is preferred.
    background_tasks.add_task(process_webhook_task, delivery_id, event_type, action, body)
    
    return {"status": "accepted"}