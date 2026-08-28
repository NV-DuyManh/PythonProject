def test_pull_requests_crud(client):
    # 1. Create a repository
    repo_response = client.post("/api/v1/repositories", json={
        "provider": "GITHUB",
        "owner": "pr-org",
        "name": "pr-repo",
        "full_name": "pr-org/pr-repo",
        "url": "https://github.com/pr-org/pr-repo"
    })
    repo_id = repo_response.json()["id"]

    # 2. Create PR
    pr_data = {
        "number": 1,
        "title": "Fix something",
        "author_username": "dev",
        "source_branch": "feat",
        "target_branch": "main",
        "head_sha": "abcdef"
    }
    response = client.post(f"/api/v1/repositories/{repo_id}/pull-requests", json=pr_data)
    assert response.status_code == 201
    pr_id = response.json()["id"]
    assert response.json()["number"] == 1
    
    # 3. Duplicate PR in same repo
    response = client.post(f"/api/v1/repositories/{repo_id}/pull-requests", json=pr_data)
    assert response.status_code == 409
    
    # 4. Get PR
    response = client.get(f"/api/v1/pull-requests/{pr_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Fix something"
    
    
    # 5. List PRs with pagination and filters
    # Create another PR
    pr_data2 = {
        "number": 2, "title": "Feat something", "author_username": "other", "source_branch": "f2", "target_branch": "main", "head_sha": "def",
        "state": "OPEN"
    }
    client.post(f"/api/v1/repositories/{repo_id}/pull-requests", json=pr_data2)
    
    response = client.get(f"/api/v1/repositories/{repo_id}/pull-requests?page_size=1&page=1")
    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert len(response.json()["items"]) == 1
    assert response.json()["pages"] == 2
    
    # Filter by state and search
    response = client.get(f"/api/v1/repositories/{repo_id}/pull-requests?state=OPEN&search=Feat")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["title"] == "Feat something"
    
    # Global PR list filter
    response = client.get(f"/api/v1/pull-requests?author=dev")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["author_username"] == "dev"
    
    # 6. Update PR
    response = client.patch(f"/api/v1/pull-requests/{pr_id}", json={"title": "Updated Title"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
