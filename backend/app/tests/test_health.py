"""
Tests for the hello world API endpoints.
"""

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to Deita API"
    assert "docs_url" in data


def test_health_check_endpoint(client: TestClient):
    """Test the health check endpoint."""
    response = client.get("/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "unhealthy"]
    assert "message" in data
    assert "version" in data
    assert "timestamp" in data
