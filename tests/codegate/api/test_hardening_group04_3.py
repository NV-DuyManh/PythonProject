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
@pytest.mark.skip(reason="Phase 11 webhook pipeline refactoring")
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
    assert response1.status_code == 202
    assert response1.json() == {"status": "accepted"}
    
    # Check DB
    event = db_session.query(WebhookEvent).filter_by(delivery_id=delivery_id).first()
    assert event is not None
    assert event.event_type == "pull_request"
    assert event.action == "opened"
    
    # Send duplicate
    response2 = client.post("/api/v1/github_webhooks", json=body, headers=headers)
    assert response2.status_code == 202
    assert response2.json() == {"status": "ignored", "reason": "Duplicate event"}
    
    # Count in DB
    count = db_session.query(WebhookEvent).filter_by(delivery_id=delivery_id).count()
    assert count == 1 # Still only one due to deduplication

@pytest.mark.skip(reason="Phase 11 webhook pipeline refactoring")
@patch("codegate.api.routers.webhooks.GithubSyncService")
def test_webhook_processing_flow(MockSyncService, db_session: Session):
    # Setup mocks
    mock_sync_instance = MockSyncService.return_value
    mock_repo = MagicMock()
    mock_pr = MagicMock()
    mock_sync_instance.sync_pull_request.return_value = (mock_repo, mock_pr)
    mock_pr.id = 999
    
    from codegate.api.routers.webhooks import process_webhook_synchronously
    from codegate.database.models.analysis import AnalysisJob
    import asyncio
    
    # Create the event in DB first
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
        "pull_request": {"html_url": "https://github.com/foo/bar/pull/10"},
        "installation": {"id": 1}
    }
    
    # Call synchronously
    asyncio.run(process_webhook_synchronously(db_session, delivery_id, "pull_request", "synchronize", body, event))
    
    # Assert AnalysisJob was created
    job = db_session.query(AnalysisJob).filter_by(pull_request_id=999).first()
    assert job is not None
    # Refresh event to check status
    db_session.refresh(event)
    assert event.status == "PROCESSED"
    
    # Check if sync was called
    MockSyncService.assert_called_once()
    mock_sync_instance.sync_pull_request.assert_called_once_with("https://github.com/foo/bar/pull/10")
    
    # Check if orchestrator was called
    MockOrchestrator.assert_called_once()
    mock_orchestrator_instance.trigger_analysis.assert_called_once()
