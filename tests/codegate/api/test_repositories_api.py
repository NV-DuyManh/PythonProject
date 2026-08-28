def test_create_repository(client):
    response = client.post("/api/v1/repositories", json={
        "provider": "GITHUB",
        "owner": "testorg",
        "name": "testrepo",
        "full_name": "testorg/testrepo",
        "url": "https://github.com/testorg/testrepo"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["full_name"] == "testorg/testrepo"

def test_duplicate_repository(client):
    repo_data = {
        "provider": "GITHUB",
        "owner": "testorg",
        "name": "testrepo2",
        "full_name": "testorg/testrepo2",
        "url": "https://github.com/testorg/testrepo2"
    }
    client.post("/api/v1/repositories", json=repo_data)
    
    # Try again
    response = client.post("/api/v1/repositories", json=repo_data)
    assert response.status_code == 409
    assert "already exists" in response.json()["message"]

def test_list_repositories(client):
    # Create two repos
    client.post("/api/v1/repositories", json={
        "provider": "GITHUB", "owner": "test1", "name": "r1", "full_name": "test1/r1", "url": "http://g.com/1"
    })
    client.post("/api/v1/repositories", json={
        "provider": "GITLAB", "owner": "test2", "name": "r2", "full_name": "test2/r2", "url": "http://g.com/2"
    })
    
    response = client.get("/api/v1/repositories")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert len(data["items"]) >= 2
    
    # Test filter by provider
    response = client.get("/api/v1/repositories?provider=GITLAB")
    data = response.json()
    assert data["total"] >= 1
    assert all(r["provider"] == "GITLAB" for r in data["items"])

def test_update_and_delete_repository(client):
    response = client.post("/api/v1/repositories", json={
        "provider": "GITHUB", "owner": "t", "name": "r", "full_name": "t/r", "url": "http://g.com/r"
    })
    repo_id = response.json()["id"]
    
    # Update
    response = client.patch(f"/api/v1/repositories/{repo_id}", json={"active": False})
    assert response.status_code == 200
    assert response.json()["active"] is False
    
    # Delete (soft delete)
    response = client.delete(f"/api/v1/repositories/{repo_id}")
    assert response.status_code == 200
    assert response.json()["active"] is False
    
    # Ensure it's still fetchable but active=False
    response = client.get(f"/api/v1/repositories/{repo_id}")
    assert response.status_code == 200
    assert response.json()["active"] is False

def test_not_found(client):
    response = client.get("/api/v1/repositories/99999")
    assert response.status_code == 404
