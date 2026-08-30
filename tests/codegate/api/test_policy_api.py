import pytest
from fastapi.testclient import TestClient
from codegate.api.main import app

client = TestClient(app)

# The tests will mock out the DB. Or use the test database in api tests.
# Since we are using standard test setup, we rely on the DB being provided by the conftest.

def test_policy_api_not_found(client):
    res = client.get("/api/v1/repositories/999999/policy")
    assert res.status_code == 404

def test_policy_evaluation_api_not_found(client):
    res = client.get("/api/v1/analyses/999999/policy")
    assert res.status_code == 404
