import pytest
import copy
from datetime import datetime
from unittest.mock import patch, MagicMock

from codegate.database.models.analysis import Status, Trigger, Severity, Source
from codegate.database.models.webhook import WebhookEvent
from codegate.integrations.pr_agent.adapter import CodeGateAdapter
from codegate.integrations.pr_agent.normalizer import PRAgentNormalizer

# 1. VERIFY MONKEY-PATCH SAFETY
def test_monkey_patch_instance_level():
    mock_reviewer1 = MagicMock()
    mock_reviewer1.git_provider = MagicMock()
    mock_reviewer2 = MagicMock()
    mock_reviewer2.git_provider = MagicMock()
    
    # Prove that patching one adapter does not patch another
    adapter1 = CodeGateAdapter("https://github.com/foo/bar/pull/1", reviewer=mock_reviewer1)
    adapter2 = CodeGateAdapter("https://github.com/foo/bar/pull/2", reviewer=mock_reviewer2)
    
    # We can't easily trigger the exact PRReviewer run without full mocks, 
    # but we can verify that the `publish_structured_review` functions are bound to different instances
    # and they capture to different `captured_structured_data` stores.
    
    # Call mock publisher directly on adapter 1
    adapter1.reviewer.git_provider.publish_structured_review({"review": "data1"})
    adapter2.reviewer.git_provider.publish_structured_review({"review": "data2"})
    
    assert adapter1.captured_structured_data == {"review": "data1"}
    assert adapter2.captured_structured_data == {"review": "data2"}
    
def test_monkey_patch_preserves_original_publish():
    mock_reviewer = MagicMock()
    mock_provider = MagicMock()
    mock_publish = MagicMock()
    mock_provider.publish_structured_review = mock_publish
    mock_reviewer.git_provider = mock_provider
    adapter = CodeGateAdapter("https://github.com/foo/bar/pull/1", reviewer=mock_reviewer)
    
    adapter.reviewer.git_provider.publish_structured_review({"review": "some_data"})
    assert adapter.captured_structured_data == {"review": "some_data"}
    # The original publisher mock should have been called
    mock_publish.assert_called_once_with({"review": "some_data"})

# 7. NORMALIZER SEVERITY/CATEGORY
def test_normalizer_deterministic_mapping():
    data = {
        "review": {
            "key_issues_to_review": [
                {"issue_header": "This is a BUG", "suggestion": "fix it"},
                {"issue_header": "security vulnerability here", "suggestion": "fix"},
                {"issue_header": "some performance issue", "suggestion": "fix"},
                {"issue_header": "typo in docs", "suggestion": "fix"},
                {"issue_header": "unknown weird issue", "suggestion": "fix"}
            ]
        }
    }
    findings = PRAgentNormalizer.normalize_findings(data)
    
    # Severity and Category check
    assert findings[0].severity == Severity.HIGH
    assert findings[0].category == "BUG"
    
    assert findings[1].severity == Severity.CRITICAL
    assert findings[1].category == "SECURITY"
    
    assert findings[2].severity == Severity.MEDIUM
    assert findings[2].category == "PERFORMANCE"
    
    assert findings[3].severity == Severity.LOW
    assert findings[3].category == "STYLE"
    
    assert findings[4].severity == Severity.MEDIUM
    assert findings[4].category == "OTHER"
    
    assert findings[0].confidence is None

# 8. TOKEN/MODEL METADATA
def test_normalizer_token_metadata():
    data = {
        "review": {"key_issues_to_review": []},
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }
    usage = PRAgentNormalizer.extract_usage(data)
    assert usage["total_tokens"] == 30
