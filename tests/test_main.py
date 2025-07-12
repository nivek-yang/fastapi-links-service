from fastapi.testclient import TestClient
from main import app


def test_health_check():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200


def test_db_check():
    client = TestClient(app)
    response = client.get("/db-check")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "MongoDB connection is successful!" in response.json()["message"]
