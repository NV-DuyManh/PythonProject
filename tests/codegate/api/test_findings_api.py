import pytest
from codegate.database.models import Finding, Severity, Source
from codegate.database.session import SessionLocal

def test_findings_list(client, db_session):
    # Setup: we have to insert a finding directly since there's no API to create one yet
    repo = client.post("/api/v1/repositories", json={"provider": "GITHUB", "owner": "f", "name": "f", "full_name": "f/f", "url": "http://f.f"}).json()
    pr = client.post(f"/api/v1/repositories/{repo['id']}/pull-requests", json={"number": 1, "title": "f", "author_username": "f", "source_branch": "f", "target_branch": "f", "head_sha": "f"}).json()
    analysis = client.post(f"/api/v1/pull-requests/{pr['id']}/analyses", json={"head_sha": "f"}).json()
    
    analysis_id = analysis["id"]
    
    f1 = Finding(analysis_run_id=analysis_id, source=Source.AI, category="Security", severity=Severity.HIGH, title="1", description="1")
    f2 = Finding(analysis_run_id=analysis_id, source=Source.RUFF, category="Style", severity=Severity.INFO, title="2", description="2")
    db_session.add(f1)
    db_session.add(f2)
    db_session.commit()
    
    # List all with pagination
    response = client.get(f"/api/v1/analyses/{analysis_id}/findings?page=1&page_size=1")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 1
    assert data["pages"] == 2
    
    # Filter by severity and source
    response = client.get(f"/api/v1/analyses/{analysis_id}/findings?severity=HIGH&source=AI")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["severity"] == "HIGH"
    
    # Filter by category
    response = client.get(f"/api/v1/analyses/{analysis_id}/findings?category=Style")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["category"] == "Style"
