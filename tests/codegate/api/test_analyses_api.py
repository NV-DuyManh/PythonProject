def test_analyses_crud(client):
    # Setup
    repo = client.post("/api/v1/repositories", json={"provider": "GITHUB", "owner": "a", "name": "a", "full_name": "a/a", "url": "http://a.a"}).json()
    pr = client.post(f"/api/v1/repositories/{repo['id']}/pull-requests", json={"number": 1, "title": "t", "author_username": "u", "source_branch": "s", "target_branch": "t", "head_sha": "abc"}).json()
    pr_id = pr["id"]

    # Create analysis
    response = client.post(f"/api/v1/pull-requests/{pr_id}/analyses", json={"head_sha": "abc"})
    assert response.status_code == 201
    analysis_id = response.json()["id"]
    assert response.json()["status"] == "PENDING"
    assert response.json()["trigger"] == "MANUAL"
    
    # List by PR
    response = client.get(f"/api/v1/pull-requests/{pr_id}/analyses")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    
    # Get single
    response = client.get(f"/api/v1/analyses/{analysis_id}")
    assert response.status_code == 200
    assert response.json()["head_sha"] == "abc"
