"""
Tests for the health check and basic application startup.
"""

def test_health_check(client):
    """Health endpoint returns 200 with status information."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0.0"
    assert "environment" in data
    assert "status" in data


def test_docs_available_in_development(client):
    """API docs are available in development mode."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_unknown_endpoint_returns_404(client):
    """Requests to unknown endpoints return 404."""
    response = client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
