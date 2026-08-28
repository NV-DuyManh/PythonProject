def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"

def test_info(client):
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    assert response.json()["name"] == "CodeGate API"

def test_openapi(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    paths = data["paths"]
    
    # Check that main routes exist
    assert any("/repositories" in path for path in paths)
    assert any("/pull-requests" in path for path in paths)
    assert any("/analyses" in path for path in paths)
    assert any("/findings" in path for path in paths)
    assert any("/health" in path for path in paths)

def test_docs(client):
    response = client.get("/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text
