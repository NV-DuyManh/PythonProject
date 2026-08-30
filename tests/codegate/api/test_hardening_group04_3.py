import pytest
import hmac
import hashlib
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from codegate.api.main import app
from codegate.api.dependencies import get_db
from codegate.database.models.webhook import WebhookEvent
from codegate.database.models.pull_request import PullRequest
from codegate.database.models.repository import Repository

client = TestClient(app)

# 4. WEBHOOK EVENT LIFECYCLE & 5. WEBHOOK DEDUP
def test_webhook_event_lifecycle_and_dedup(db_session: Session):
    app.dependency_overrides[get_db] = lambda: db_session
    # This will verify the webhook dedup using DB UniqueConstraint indirectly,
    # because if we insert exactly the same provider & delivery_id, it should return ignored.
    delivery_id = "test-delivery-id-lifecycle-999"
    
    body = {
        "action": "opened",
        "pull_request": {"number": 99, "html_url": "https://github.com/foo/bar/pull/99"},
        "repository": {"full_name": "foo/bar"}
    }
    
    # Calculate signature
    import hmac
    import hashlib
    import json
    
    secret = "codegate-secret".encode()
    payload = json.dumps(body, separators=(',', ':')).encode("utf-8")
    signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    
    headers = {
        "X-GitHub-Event": "pull_request",
        "X-GitHub-Delivery": delivery_id,
        "X-Hub-Signature-256": f"sha256={signature}"
    }
    
    # Send the first one
    response1 = client.post("/api/v1/github_webhooks", json=body, headers=headers)
    assert response1.status_code == 200
    assert response1.json() == {"status": "accepted"}
    
    # Check DB
    event = db_session.query(WebhookEvent).filter_by(delivery_id=delivery_id).first()
    assert event is not None
    assert event.event_type == "pull_request"
    assert event.action == "opened"
    
    # Send duplicate
    response2 = client.post("/api/v1/github_webhooks", json=body, headers=headers)
    assert response2.status_code == 200
    assert response2.json() == {"status": "ignored", "reason": "Duplicate event"}
    
    # Count in DB
    count = db_session.query(WebhookEvent).filter_by(delivery_id=delivery_id).count()
    assert count == 1 # Still only one due to deduplication

@patch("codegate.api.routers.webhooks.GithubSyncService")
@patch("codegate.api.routers.webhooks.AnalysisOrchestrator")
def test_webhook_processing_flow(MockOrchestrator, MockSyncService, db_session: Session):
    # Setup mocks
    mock_sync_instance = MockSyncService.return_value
    mock_repo = MagicMock()
    mock_pr = MagicMock()
    mock_sync_instance.sync_pull_request.return_value = (mock_repo, mock_pr)
    
    mock_orchestrator_instance = MockOrchestrator.return_value
    
    from unittest.mock import AsyncMock
    mock_orchestrator_instance.trigger_analysis = AsyncMock()
    
    from codegate.api.routers.webhooks import process_webhook_task
    import asyncio
    
    # Create the event in DB first because process_webhook_task expects it
    delivery_id = "test-processing-flow-123"
    event = WebhookEvent(
        provider="github",
        delivery_id=delivery_id,
        event_type="pull_request",
        action="synchronize",
        payload_hash="hash"
    )
    db_session.add(event)
    db_session.commit()
    
    body = {
        "action": "synchronize",
        "pull_request": {"html_url": "https://github.com/foo/bar/pull/10"}
    }
    
    # Prevent db_session from closing when used in context manager
    original_close = db_session.close
    db_session.close = MagicMock()
    
    with patch("codegate.api.routers.webhooks.SessionLocal", return_value=db_session):
        # Call the background task synchronously using asyncio.run
        asyncio.run(process_webhook_task(delivery_id, "pull_request", "synchronize", body))
        
    db_session.close = original_close
    
    # Commit to end current transaction and start a new one to see changes from SessionLocal
    db_session.commit()
    # Refresh event to check status
    db_session.refresh(event)
    assert event.status == "PROCESSED"
    
    # Check if sync was called
    MockSyncService.assert_called_once()
    mock_sync_instance.sync_pull_request.assert_called_once_with("https://github.com/foo/bar/pull/10")
    
    # Check if orchestrator was called
    MockOrchestrator.assert_called_once()
    mock_orchestrator_instance.trigger_analysis.assert_called_once()
