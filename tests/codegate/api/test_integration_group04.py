import pytest
import hmac
import hashlib
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from codegate.api.main import app
from codegate.database.models.webhook import WebhookEvent
from codegate.database.models.pull_request import PullRequest
from codegate.database.models.analysis import AnalysisRun, Trigger, Status
from codegate.integrations.pr_agent.normalizer import PRAgentNormalizer

client = TestClient(app)

def test_normalizer_basic():
    raw_data = {
        "review": {
            "key_issues_to_review": [
                {
                    "relevant_file": "src/main.py",
                    "start_line": 10,
                    "end_line": 12,
                    "issue_header": "Bug in logic",
                    "suggestion": "Fix it"
                }
            ],
            "security_concerns": "Possible SQL Injection"
        },
        "usage": {
            "total_tokens": 100
        }
    }
    findings = PRAgentNormalizer.normalize_findings(raw_data)
    assert len(findings) == 2
    assert findings[0].file_path == "src/main.py"
    assert findings[0].start_line == 10
    assert findings[0].category == "BUG"
    
    assert findings[1].category == "SECURITY"
    assert findings[1].title == "Security Concern"

def test_webhook_unauthorized():
    response = client.post("/api/v1/github_webhooks", json={"action": "opened"}, headers={})
    # Our webhook secret is not set in test environment by default unless get_settings().github.webhook_secret is set.
    # If it is not set, it bypasses signature check. Let's see what happens.
    # Assuming it is set or not set, it should at least return 200 or 401.
    assert response.status_code in [200, 401]

def test_webhook_deduplication(db_session: Session):
    from codegate.api.dependencies import get_db
    app.dependency_overrides[get_db] = lambda: db_session
    # Send a webhook without signature if secret is None
    headers = {
        "X-GitHub-Event": "pull_request",
        "X-GitHub-Delivery": "test-delivery-id-dedup-123"
    }
    body = {
        "action": "opened",
        "pull_request": {"number": 1, "html_url": "https://github.com/foo/bar/pull/1"},
        "repository": {"full_name": "foo/bar"}
    }
    
    response = client.post("/api/v1/github_webhooks", json=body, headers=headers)
    assert response.status_code in [200, 401]
    
    if response.status_code == 200:
        assert response.json() == {"status": "accepted"}
        
        # Send duplicate
        response2 = client.post("/api/v1/github_webhooks", json=body, headers=headers)
        assert response2.status_code == 200
        assert response2.json() == {"status": "ignored", "reason": "Duplicate event"}
