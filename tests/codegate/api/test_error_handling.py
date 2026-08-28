def test_session_rollback_on_conflict(client):
    repo_data = {
        "provider": "GITHUB",
        "owner": "err-org",
        "name": "err-repo",
        "full_name": "err-org/err-repo",
        "url": "https://github.com/err-org/err-repo"
    }
    # 1. Successful creation
    response1 = client.post("/api/v1/repositories", json=repo_data)
    assert response1.status_code == 201
    
    # 2. Conflict creation (should fail and rollback)
    response2 = client.post("/api/v1/repositories", json=repo_data)
    assert response2.status_code == 409
    
    # 3. Next request should succeed because session was rolled back and closed properly
    repo_data["name"] = "err-repo-2"
    repo_data["full_name"] = "err-org/err-repo-2"
    response3 = client.post("/api/v1/repositories", json=repo_data)
    assert response3.status_code == 201
